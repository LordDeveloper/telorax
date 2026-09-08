package com.telorax.agent

import android.content.Context
import android.content.Intent
import android.net.Uri
import org.json.JSONObject

class WireGuardBridge(private val context: Context) {
    fun apply(config: JSONObject): String {
        if (!config.optBoolean("enabled", false)) {
            return "wireguard disabled"
        }
        val text = config.optString("config_text")
        if (text.isBlank()) {
            return "wireguard config missing"
        }
        val uri = Uri.parse("https://telorax.local/import-wireguard")
        val intent = Intent(Intent.ACTION_VIEW, uri)
            .setPackage("com.wireguard.android")
            .putExtra("config", text)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        return try {
            context.startActivity(intent)
            "wireguard import intent sent"
        } catch (_: Exception) {
            "install WireGuard app and retry tunnel setup"
        }
    }
}
