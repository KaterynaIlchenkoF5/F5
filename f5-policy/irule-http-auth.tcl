# iRule: forward APM HTTP-Auth requests to the SQL auth service pool
# Attach to the virtual server that carries APM HTTP-Auth traffic.

when HTTP_REQUEST {
    if { [HTTP::uri] starts_with "/auth" } {
        pool sql_auth_service_pool
    }
}
