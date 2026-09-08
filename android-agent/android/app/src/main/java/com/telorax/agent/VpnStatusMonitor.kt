package com.telorax.agent

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities

object VpnStatusMonitor {
    fun isVpnActive(context: Context): Boolean {
        return try {
            val manager = context.getSystemService(ConnectivityManager::class.java) ?: return false
            val network = manager.activeNetwork ?: return false
            val capabilities = manager.getNetworkCapabilities(network) ?: return false
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_VPN)
        } catch (_: SecurityException) {
            false
        }
    }
}
