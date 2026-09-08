package mobile

import (
	"context"
	"encoding/json"
	"time"

	"github.com/LordDeveloper/telorax/android-agent/internal/agent"
	"github.com/LordDeveloper/telorax/android-agent/internal/config"
	"github.com/LordDeveloper/telorax/android-agent/internal/telegram"
)

type Agent struct {
	runtime *agent.Runtime
}

func New(baseURL, agentID, token, version string) (*Agent, error) {
	cfg := config.Config{
		BaseURL:  baseURL,
		AgentID:  agentID,
		Token:    token,
		Version:  version,
		Platform: "android",
		Arch:     "arm64",
	}
	runtime, err := agent.NewRuntime(cfg)
	if err != nil {
		return nil, err
	}
	return &Agent{runtime: runtime}, nil
}

func (a *Agent) SetCapabilitiesJSON(raw string) string {
	var caps telegram.Capabilities
	if err := json.Unmarshal([]byte(raw), &caps); err != nil {
		return err.Error()
	}
	a.runtime.SetCapabilities(caps)
	return "ok"
}

func (a *Agent) Bootstrap() string {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	message, err := a.runtime.Bootstrap(ctx)
	if err != nil {
		return err.Error()
	}
	return message
}

func (a *Agent) Heartbeat() string {
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	status, err := a.runtime.Heartbeat(ctx)
	if err != nil {
		return err.Error()
	}
	return status
}

func (a *Agent) WireGuardConfig() string {
	return a.runtime.WireGuardConfig()
}

func (a *Agent) TelegramReady() bool {
	return a.runtime.TelegramReady()
}

func (a *Agent) CheckUpdateJSON() string {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	result, err := a.runtime.CheckUpdate(ctx)
	if err != nil {
		return mustJSON(map[string]string{"error": err.Error()})
	}
	return mustJSON(result)
}

func mustJSON(value any) string {
	raw, err := json.Marshal(value)
	if err != nil {
		return `{"error":"json marshal failed"}`
	}
	return string(raw)
}
