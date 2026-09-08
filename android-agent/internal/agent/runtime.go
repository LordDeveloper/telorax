package agent

import (
	"context"
	"fmt"
	"time"

	"github.com/LordDeveloper/telorax/android-agent/internal/api"
	"github.com/LordDeveloper/telorax/android-agent/internal/config"
	"github.com/LordDeveloper/telorax/android-agent/internal/telegram"
	"github.com/LordDeveloper/telorax/android-agent/internal/tunnel"
	"github.com/LordDeveloper/telorax/android-agent/internal/update"
)

type Runtime struct {
	cfg      config.Config
	client   *api.Client
	tunnel   *tunnel.Manager
	updater  *update.Manager
	caps     telegram.Capabilities
	status   string
}

func NewRuntime(cfg config.Config) (*Runtime, error) {
	if err := cfg.Valid(); err != nil {
		return nil, err
	}
	client := api.NewClient(cfg)
	return &Runtime{
		cfg:     cfg,
		client:  client,
		tunnel:  tunnel.NewManager(),
		updater: update.NewManager(client),
		status:  "initialized",
	}, nil
}

func (r *Runtime) SetCapabilities(caps telegram.Capabilities) {
	r.caps = caps
}

func (r *Runtime) Bootstrap(ctx context.Context) (string, error) {
	registered, err := r.client.Register(ctx, api.RegisterRequest{
		Platform:     r.cfg.Platform,
		Arch:         r.cfg.Arch,
		Version:      r.cfg.Version,
		Capabilities: r.caps.ToAPI(),
	})
	if err != nil {
		return "", err
	}

	remote, err := r.client.FetchConfig(ctx)
	if err != nil {
		return "", err
	}

	wgConfig, err := r.tunnel.Apply(remote.WireGuard)
	if err != nil {
		return "", err
	}

	r.status = "registered"
	message := fmt.Sprintf("registered as %s; tunnel_ready=%t", registered.DeviceID, r.tunnel.Active())
	if wgConfig != "" && remote.WireGuard.Enabled {
		message += "; wireguard_config_ready"
	}
	return message, nil
}

func (r *Runtime) Heartbeat(ctx context.Context) (string, error) {
	resp, err := r.client.Heartbeat(ctx, api.HeartbeatRequest{
		Status:       r.status,
		Capabilities: r.caps.ToAPI(),
		TunnelUp:     r.tunnel.Active(),
	})
	if err != nil {
		return "", err
	}
	return resp.Status, nil
}

func (r *Runtime) CheckUpdate(ctx context.Context) (update.Result, error) {
	return r.updater.Check(ctx, r.cfg.Version)
}

func (r *Runtime) WireGuardConfig() string {
	return r.tunnel.LastConfig()
}

func (r *Runtime) TelegramReady() bool {
	return r.caps.ReadyForAutomation()
}

func (r *Runtime) Status() string {
	return r.status
}

func (r *Runtime) RunHeartbeatLoop(ctx context.Context, interval time.Duration, onTick func(string)) error {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			status, err := r.Heartbeat(ctx)
			if err != nil {
				return err
			}
			if onTick != nil {
				onTick(status)
			}
		}
	}
}
