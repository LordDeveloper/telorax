package com.telorax.agent

import kotlinx.coroutines.delay
import org.json.JSONObject

class SignupOrchestrator(
    private val api: AgentApiClient,
) {
    suspend fun runClaimedJob(jobJson: JSONObject): String {
        val job = SignupJob(
            id = jobJson.getInt("id"),
            msisdn = jobJson.getLong("msisdn"),
            firstName = jobJson.getString("first_name"),
            lastName = jobJson.getString("last_name"),
        )
        api.patchJobMetadata(
            job.id,
            mapOf("stage" to "telegram_signup_started"),
        )
        val service = TeloraxAccessibilityService.requireService()
        TelegramUiAutomator.runSignup(service, job) {
            waitForSmsCode(job.id)
        }
        api.patchJobMetadata(
            job.id,
            mapOf("stage" to "signup_ui_completed"),
        )
        return "Signup UI completed for job #${job.id}"
    }

    private suspend fun waitForSmsCode(jobId: Int): String {
        api.patchJobMetadata(jobId, mapOf("stage" to "waiting_sms_code"))
        repeat(90) {
            val payload = api.getJob(jobId)
            val metadata = payload.optJSONObject("metadata") ?: JSONObject()
            val code = metadata.optString("sms_code").ifBlank {
                metadata.optString("verification_code")
            }
            if (code.isNotBlank()) {
                api.patchJobMetadata(jobId, mapOf("stage" to "sms_code_received"))
                return code
            }
            delay(2_000)
        }
        throw IllegalStateException("Timed out waiting for sms_code from server")
    }
}
