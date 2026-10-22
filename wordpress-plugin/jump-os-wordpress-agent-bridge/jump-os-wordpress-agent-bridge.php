<?php
/**
 * Plugin Name: Jump OS WordPress Agent Bridge
 * Description: Tenant-scoped, token-authenticated capabilities for approved human and AI operators.
 * Version: 0.3.1
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Author: Christopher Amaya
 * License: MIT
 * License URI: https://opensource.org/license/mit
 * Text Domain: jump-os-wordpress-agent-bridge
 */

defined( 'ABSPATH' ) || exit;

final class Jump_OS_WordPress_Agent_Bridge {
    const OPTION = 'jump_os_agent_bridge_settings';
    const REST_NAMESPACE = 'jump-os-agent/v1';

    public static function boot() {
        add_action( 'rest_api_init', array( __CLASS__, 'register_routes' ) );
        add_action( 'admin_menu', array( __CLASS__, 'register_settings_page' ) );
        add_action( 'admin_init', array( __CLASS__, 'register_settings' ) );
    }

    public static function settings() {
        $saved = get_option( self::OPTION, array() );
        return wp_parse_args(
            is_array( $saved ) ? $saved : array(),
            array(
                'viewer_token_hash'   => '',
                'operator_token_hash' => '',
                'allowed_plugins'     => array(),
            )
        );
    }

    public static function register_settings_page() {
        add_options_page(
            'Jump OS Agent Bridge',
            'Jump OS Agent Bridge',
            'manage_options',
            'jump-os-agent-bridge',
            array( __CLASS__, 'render_settings_page' )
        );
    }

    public static function register_settings() {
        register_setting(
            'jump_os_agent_bridge',
            self::OPTION,
            array( 'sanitize_callback' => array( __CLASS__, 'sanitize_settings' ) )
        );
    }

    public static function sanitize_settings( $input ) {
        $current = self::settings();
        $input = is_array( $input ) ? $input : array();
        $settings = $current;
        foreach ( array( 'viewer_token', 'operator_token' ) as $field ) {
            if ( ! empty( $input[ $field ] ) ) {
                $settings[ $field . '_hash' ] = wp_hash_password( (string) $input[ $field ] );
            }
        }
        $plugins = preg_split( '/\r\n|\r|\n/', (string) ( $input['allowed_plugins'] ?? '' ) );
        $settings['allowed_plugins'] = array_values( array_unique( array_filter( array_map( array( __CLASS__, 'valid_plugin_file' ), $plugins ) ) ) );
        return $settings;
    }

    public static function valid_plugin_file( $plugin ) {
        $plugin = trim( (string) $plugin );
        if ( ! preg_match( '#^[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+\.php$#', $plugin ) || validate_file( $plugin ) !== 0 ) {
            return '';
        }
        return $plugin;
    }

    public static function render_settings_page() {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }
        $settings = self::settings();
        ?>
        <div class="wrap">
            <h1>Jump OS WordPress Agent Bridge</h1>
            <p>Create two long random tokens outside this screen. Entering a non-empty token replaces its stored hash; tokens are never displayed again.</p>
            <form method="post" action="options.php">
                <?php settings_fields( 'jump_os_agent_bridge' ); ?>
                <table class="form-table" role="presentation">
                    <tr><th scope="row"><label for="viewer_token">Viewer token</label></th><td><input id="viewer_token" name="<?php echo esc_attr( self::OPTION ); ?>[viewer_token]" type="password" class="regular-text" autocomplete="new-password" /><p class="description">Status and capability discovery only.</p></td></tr>
                    <tr><th scope="row"><label for="operator_token">Operator token</label></th><td><input id="operator_token" name="<?php echo esc_attr( self::OPTION ); ?>[operator_token]" type="password" class="regular-text" autocomplete="new-password" /><p class="description">Only the explicitly listed activation operations.</p></td></tr>
                    <tr><th scope="row"><label for="allowed_plugins">Approved plugin files</label></th><td><textarea id="allowed_plugins" name="<?php echo esc_attr( self::OPTION ); ?>[allowed_plugins]" rows="8" class="large-text code"><?php echo esc_textarea( implode( "\n", $settings['allowed_plugins'] ) ); ?></textarea><p class="description">One installed plugin file per line, for example <code>elementor/elementor.php</code>. No wildcard or directory paths.</p></td></tr>
                </table>
                <?php submit_button(); ?>
            </form>
            <p><strong>Update safety:</strong> this base plugin does not update plugins. A portable plugin cannot truthfully promise a verified provider backup. Use the host gateway adapter or the provider's own backup-and-update flow when maintenance is required.</p>
        </div>
        <?php
    }

    public static function register_routes() {
        register_rest_route( self::REST_NAMESPACE, '/capabilities', array(
            'methods'             => WP_REST_Server::READABLE,
            'permission_callback' => array( __CLASS__, 'viewer_permission' ),
            'callback'            => array( __CLASS__, 'capabilities' ),
        ) );
        register_rest_route( self::REST_NAMESPACE, '/status', array(
            'methods'             => WP_REST_Server::READABLE,
            'permission_callback' => array( __CLASS__, 'viewer_permission' ),
            'callback'            => array( __CLASS__, 'status' ),
        ) );
        register_rest_route( self::REST_NAMESPACE, '/operations/(?P<operation>[a-z][a-z0-9-]{0,63})', array(
            'methods'             => WP_REST_Server::CREATABLE,
            'permission_callback' => array( __CLASS__, 'operator_permission' ),
            'callback'            => array( __CLASS__, 'run_operation' ),
            'args'                => array( 'operation' => array( 'sanitize_callback' => 'sanitize_key' ) ),
        ) );
    }

    public static function viewer_permission( WP_REST_Request $request ) {
        return self::authorize( $request, 'viewer' );
    }

    public static function operator_permission( WP_REST_Request $request ) {
        return self::authorize( $request, 'operator' );
    }

    private static function authorize( WP_REST_Request $request, $required_role ) {
        $header = (string) $request->get_header( 'authorization' );
        if ( 0 !== stripos( $header, 'Bearer ' ) ) {
            return new WP_Error( 'jump_os_unauthorized', 'A bearer token is required.', array( 'status' => 401 ) );
        }
        $token = trim( substr( $header, 7 ) );
        $settings = self::settings();
        $role = '';
        if ( $token && ! empty( $settings['operator_token_hash'] ) && wp_check_password( $token, $settings['operator_token_hash'] ) ) {
            $role = 'operator';
        } elseif ( $token && ! empty( $settings['viewer_token_hash'] ) && wp_check_password( $token, $settings['viewer_token_hash'] ) ) {
            $role = 'viewer';
        }
        if ( ! $role || ( 'operator' === $required_role && 'operator' !== $role ) ) {
            return new WP_Error( 'jump_os_unauthorized', 'The supplied token is not authorized for this capability.', array( 'status' => 401 ) );
        }
        return true;
    }

    private static function operation_map() {
        $operations = array();
        foreach ( self::settings()['allowed_plugins'] as $plugin ) {
            $base = strtolower( pathinfo( $plugin, PATHINFO_FILENAME ) );
            $base = preg_replace( '/[^a-z0-9]+/', '-', $base );
            $base = trim( $base, '-' );
            $activate = 'plugin-' . $base . '-activate';
            if ( isset( $operations[ $activate ] ) ) {
                $activate .= '-' . substr( hash( 'sha256', $plugin ), 0, 8 );
            }
            $operations[ $activate ] = array( 'plugin' => $plugin, 'kind' => 'activate' );
        }
        ksort( $operations );
        return $operations;
    }

    public static function capabilities() {
        return rest_ensure_response( array(
            'ok'         => true,
            'operations' => array_map(
                static function ( $operation_id ) {
                    return array( 'id' => $operation_id, 'method' => 'POST', 'minimum_role' => 'operator' );
                },
                array_keys( self::operation_map() )
            ),
        ) );
    }

    public static function status() {
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        $updates = get_site_transient( 'update_plugins' );
        $plugins = array();
        foreach ( self::settings()['allowed_plugins'] as $plugin ) {
            $absolute = WP_PLUGIN_DIR . '/' . $plugin;
            $installed = file_exists( $absolute );
            $data = $installed ? get_plugin_data( $absolute, false, false ) : array();
            $plugins[] = array(
                'file'           => $plugin,
                'installed'      => $installed,
                'active'         => $installed && is_plugin_active( $plugin ),
                'version'        => $installed ? (string) $data['Version'] : null,
                'pending_update' => is_object( $updates ) && isset( $updates->response[ $plugin ] ),
            );
        }
        return rest_ensure_response( array( 'ok' => true, 'wordpress_version' => get_bloginfo( 'version' ), 'plugins' => $plugins ) );
    }

    public static function run_operation( WP_REST_Request $request ) {
        if ( $request->get_body() && '{}' !== trim( $request->get_body() ) ) {
            return new WP_Error( 'jump_os_arguments_forbidden', 'Operations accept no arguments.', array( 'status' => 400 ) );
        }
        $operation_id = (string) $request['operation'];
        $operation = self::operation_map()[ $operation_id ] ?? null;
        if ( ! $operation || 'activate' !== $operation['kind'] ) {
            return new WP_Error( 'jump_os_operation_not_found', 'This operation is not available.', array( 'status' => 404 ) );
        }
        $result = activate_plugin( $operation['plugin'], '', false, true );
        if ( is_wp_error( $result ) ) {
            return $result;
        }
        return rest_ensure_response( array( 'ok' => true, 'operation' => $operation_id, 'result' => array( 'plugin' => $operation['plugin'], 'active' => is_plugin_active( $operation['plugin'] ) ) ) );
    }
}

Jump_OS_WordPress_Agent_Bridge::boot();
