package com.telorax.agent

import org.json.JSONArray
import org.json.JSONObject

data class AmneziaConfig(
    val profileName: String,
    val rawJson: String,
    val apiEndpoint: String?,
    val wireguardText: String?,
    val protocol: String,
)

object AmneziaConfigParser {
    fun parse(text: String): AmneziaConfig {
        val trimmed = text.trim()
        if (trimmed.startsWith("{")) {
            return parseJson(trimmed)
        }
        if (trimmed.contains("[Interface]")) {
            return AmneziaConfig(
                profileName = "Imported WireGuard",
                rawJson = trimmed,
                apiEndpoint = null,
                wireguardText = trimmed,
                protocol = "wireguard",
            )
        }
        throw IllegalArgumentException("Unsupported config format")
    }

    private fun parseJson(raw: String): AmneziaConfig {
        val root = JSONObject(raw)
        val name = root.optString("name", "Amnezia Profile")
        val apiEndpoint = root.optString("apiEndpoint").ifBlank { null }
        val containers = root.optJSONArray("containers") ?: JSONArray()
        var wireguardText: String? = null
        var protocol = "unknown"

        for (index in 0 until containers.length()) {
            val container = containers.optJSONObject(index) ?: continue
            val containerType = container.optString("container", "")
            protocol = containerType.ifBlank { protocol }
            val lastConfig = container.optString("last_config").ifBlank { null }
            if (lastConfig != null && lastConfig.contains("[Interface]")) {
                wireguardText = lastConfig
                break
            }
            val awg = container.optJSONObject("awg")
            if (awg != null) {
                wireguardText = buildAwgConfig(awg, container)
                protocol = "amnezia-awg"
                break
            }
        }

        return AmneziaConfig(
            profileName = name,
            rawJson = raw,
            apiEndpoint = apiEndpoint,
            wireguardText = wireguardText,
            protocol = protocol,
        )
    }

    private fun buildAwgConfig(awg: JSONObject, container: JSONObject): String? {
        val lastConfig = container.optString("last_config").ifBlank { null }
        if (lastConfig != null) {
            return lastConfig
        }
        val interfaceBlock = awg.optJSONObject("interface") ?: return null
        val peerBlock = awg.optJSONObject("peer") ?: return null
        return buildString {
            appendLine("[Interface]")
            interfaceBlock.keys().forEach { key ->
                appendLine("$key = ${interfaceBlock.get(key)}")
            }
            appendLine()
            appendLine("[Peer]")
            peerBlock.keys().forEach { key ->
                appendLine("$key = ${peerBlock.get(key)}")
            }
        }.trim()
    }
}
