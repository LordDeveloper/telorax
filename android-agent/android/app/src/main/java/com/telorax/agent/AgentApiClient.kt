package com.telorax.agent

import android.content.Context
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.File
import java.util.concurrent.TimeUnit

class AgentApiClient(
    context: Context,
    private val prefs: Prefs,
) {
    private val appContext = context.applicationContext
    private val client = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val jsonType = "application/json; charset=utf-8".toMediaType()

    fun claimJob(): JSONObject? {
        val payload = JSONObject().put("provider", "android-agent")
        val response = post("/v1/provisioning/agent/claim", payload)
        return if (response.code == 204) null else JSONObject(response.body?.string().orEmpty())
    }

    fun getJob(jobId: Int): JSONObject {
        val response = get("/v1/provisioning/agent/jobs/$jobId")
        return JSONObject(response.body?.string().orEmpty())
    }

    fun patchJobMetadata(jobId: Int, metadata: Map<String, Any?>): JSONObject {
        val payload = JSONObject()
        metadata.forEach { (key, value) -> payload.put(key, value) }
        val response = patch("/v1/provisioning/agent/jobs/$jobId/metadata", payload)
        return JSONObject(response.body?.string().orEmpty())
    }

    fun failJob(jobId: Int, reason: String) {
        val payload = JSONObject().put("reason", reason)
        post("/v1/provisioning/agent/jobs/$jobId/fail", payload)
    }

    fun completeJob(jobId: Int, sessionFile: File): JSONObject {
        val body = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                sessionFile.name,
                sessionFile.asRequestBody("application/octet-stream".toMediaType()),
            )
            .build()
        val request = headers()
            .url("${baseUrl()}/v1/provisioning/agent/jobs/$jobId/complete")
            .post(body)
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IllegalStateException("complete failed: ${response.code}")
            }
            return JSONObject(response.body?.string().orEmpty())
        }
    }

    private fun baseUrl(): String = prefs.effectiveBaseUrl(appContext)

    private fun headers(): Request.Builder =
        Request.Builder()
            .addHeader("X-Telorax-Agent-Id", prefs.agentId)
            .addHeader("X-Telorax-Agent-Token", prefs.agentToken)

    private fun get(path: String) =
        client.newCall(headers().url("${baseUrl()}$path").get().build()).execute()

    private fun post(path: String, payload: JSONObject) =
        client.newCall(
            headers()
                .url("${baseUrl()}$path")
                .addHeader("Content-Type", "application/json")
                .post(payload.toString().toRequestBody(jsonType))
                .build(),
        ).execute()

    private fun patch(path: String, payload: JSONObject) =
        client.newCall(
            headers()
                .url("${baseUrl()}$path")
                .addHeader("Content-Type", "application/json")
                .patch(payload.toString().toRequestBody(jsonType))
                .build(),
        ).execute()
}
