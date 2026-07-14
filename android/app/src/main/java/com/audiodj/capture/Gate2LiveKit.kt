package com.audiodj.capture

import android.content.Context
import android.media.AudioManager
import android.os.Build
import io.livekit.android.AudioOptions
import io.livekit.android.LiveKit
import io.livekit.android.LiveKitOverrides
import io.livekit.android.audio.NoAudioHandler
import io.livekit.android.events.RoomEvent
import io.livekit.android.events.collect
import io.livekit.android.room.Room
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Gate 2 — Android connects to LiveKit as DJ but publishes NOTHING.
 * NO MediaProjection, NO RECORD_AUDIO runtime prompt, NO foreground service, NO tracks.
 * NoAudioHandler => room connect must not grab audio focus / change the Bluetooth route.
 * Logs AudioManager mode + Bluetooth route before/after so we can isolate any RTC side effect.
 */
class Gate2LiveKit(private val ctx: Context, private val log: (String) -> Unit) {
    private var room: Room? = null

    fun audioSnapshot(tag: String) {
        val am = ctx.getSystemService(Context.AUDIO_SERVICE) as AudioManager
        val mode = when (am.mode) {
            AudioManager.MODE_NORMAL -> "NORMAL"
            AudioManager.MODE_IN_COMMUNICATION -> "IN_COMMUNICATION"
            AudioManager.MODE_IN_CALL -> "IN_CALL"
            else -> am.mode.toString()
        }
        val dev = if (Build.VERSION.SDK_INT >= 31)
            am.communicationDevice?.type?.toString() ?: "null" else "n/a<31"
        log("[audio:$tag] mode=$mode musicActive=${am.isMusicActive} commDevice=$dev")
    }

    fun connect(scope: CoroutineScope, tokenApi: String) {
        audioSnapshot("before-connect")
        scope.launch {
            try {
                val (url, token) = withContext(Dispatchers.IO) { fetchToken(tokenApi) }
                log("got DJ token; connecting -> $url")
                val r = LiveKit.create(
                    ctx.applicationContext,
                    overrides = LiveKitOverrides(
                        audioOptions = AudioOptions(audioHandler = NoAudioHandler()),
                    ),
                )
                room = r
                scope.launch {
                    r.events.collect { e ->
                        when (e) {
                            is RoomEvent.Disconnected -> log("[lk] event: disconnected reason=${e.reason}")
                            is RoomEvent.Reconnecting -> log("[lk] event: reconnecting")
                            is RoomEvent.Reconnected -> log("[lk] event: reconnected")
                            else -> {}
                        }
                    }
                }
                r.connect(url, token)
                val lp = r.localParticipant
                log("[lk] CONNECTED state=${r.state} identity=${lp.identity} canPublish=${lp.permissions?.canPublish} publishedTracks=${lp.trackPublications.size}")
                audioSnapshot("after-connect")
            } catch (e: Exception) {
                log("[lk] connect FAILED: ${e.javaClass.simpleName}: ${e.message}")
            }
        }
    }

    fun disconnect() {
        room?.disconnect()
        room = null
        log("[lk] disconnect() called")
        audioSnapshot("after-disconnect")
    }

    private fun fetchToken(api: String): Pair<String, String> {
        val conn = URL("$api?role=dj&identity=pixel-host").openConnection() as HttpURLConnection
        conn.connectTimeout = 5000
        conn.readTimeout = 5000
        val body = conn.inputStream.bufferedReader().readText()
        conn.disconnect()
        val j = JSONObject(body)
        return j.getString("url") to j.getString("token")
    }
}
