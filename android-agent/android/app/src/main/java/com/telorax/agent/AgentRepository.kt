package com.telorax.agent

import android.content.Context
import android.provider.Settings
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class AgentRepository(
    private val context: Context,
    private val prefs: Prefs,
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val jsonType = "application/json; charset=utf-8".toMediaType()

    fun bootstrap(capabilities: JSONObject): JSONObject {
        val payload = JSONObject()
            .put("platform", "android")
            .put("arch", "arm64")
            .put("version", BuildConfig.VERSION_NAME)
            .put("capabilities", capabilities)
        return post("/v1/mobile-agent/register", payload)
    }

    fun heartbeat(status: String, capabilities: JSONObject, tunnelUp: Boolean): JSONObject {
        val payload = JSONObject()
            .put("status", status)
            .put("capabilities", capabilities)
            .put("tunnel_up", tunnelUp)
        return post("/v1/mobile-agent/heartbeat", payload)
    }

    fun fetchConfig(): JSONObject = get("/v1/mobile-agent/config")

    fun checkUpdate(): JSONObject =
        get("/v1/mobile-agent/updates/check?version=${BuildConfig.VERSION_NAME}&platform=android&arch=arm64")

    private fun headers(): Request.Builder {
        return Request.Builder()
            .addHeader("Content-Type", "application/json")
            .addHeader("X-Telorax-Agent-Id", prefs.agentId)
            .addHeader("X-Telorax-Agent-Token", prefs.agentToken)
    }

    private fun post(path: String, payload: JSONObject): JSONObject {
        val request = headers()
            .url("${prefs.baseUrl}$path")
            .post(payload.toString().toRequestBody(jsonType))
            .build()
        return execute(request)
    }

    private fun get(path: String): JSONObject {
        val request = headers()
            .url("${prefs.baseUrl}$path")
            .get()
            .build()
        return execute(request)
    }

    private fun execute(request: Request): JSONObject {
        client.newCall(request).execute().use { response ->
            val body = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                throw IllegalStateException("API ${response.code}: $body")
            }
            return if (body.isBlank()) JSONObject() else JSONObject(body)
        }
    }
}

class Prefs(context: Context) {
    private val storage = context.getSharedPreferences("telorax_agent", Context.MODE_PRIVATE)

    var baseUrl: String
        get() = storage.getString("base_url", "http://10.8.0.1:8000") ?: "http://10.8.0.1:8000"
        set(value) { storage.edit().putString("base_url", value).apply() }

    var agentId: String
        get() = storage.getString("agent_id", "android-01") ?: "android-01"
        set(value) { storage.edit().putString("agent_id", value).apply() }

    var agentToken: String
        get() = storage.getString("agent_token", "") ?: ""
        set(value) { storage.edit().putString("agent_token", value).apply() }
}

object CapabilityProbe {
    fun collect(context: Context): JSONObject {
        val installed = TelegramProbe.isInstalled(context)
        val accessibilityEnabled = TeloraxAccessibilityService.isEnabled(context)
        val canObserve = TeloraxAccessibilityService.canObserveUi()
        val canPerform = TeloraxAccessibilityService.canPerformActions()
        val notes = when {
            !installed -> "official Telegram app is not installed"
            !accessibilityEnabled -> "enable Telorax accessibility service"
            !canObserve -> "waiting for Telegram UI observation"
            !canPerform -> "waiting for Telegram action capability"
            else -> "telegram automation prerequisites satisfied"
        }
        return JSONObject()
            .put("package_installed", installed)
            .put("accessibility_enabled", accessibilityEnabled)
            .put("can_observe_ui", canObserve)
            .put("can_perform_actions", canPerform)
            .put("notes", notes)
    }
}

object TelegramProbe {
    fun isInstalled(context: Context): Boolean {
        return try {
            context.packageManager.getPackageInfo("org.telegram.messenger", 0)
            true
        } catch (_: Exception) {
            false
        }
    }
}
