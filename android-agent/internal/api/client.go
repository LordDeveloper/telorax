package api

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/LordDeveloper/telorax/android-agent/internal/config"
)

type Client struct {
	cfg    config.Config
	client *http.Client
}

func NewClient(cfg config.Config) *Client {
	return &Client{
		cfg: cfg,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

func (c *Client) headers() http.Header {
	headers := make(http.Header)
	headers.Set("Content-Type", "application/json")
	headers.Set("User-Agent", c.cfg.UserAgent)
	headers.Set("X-Telorax-Agent-Id", c.cfg.AgentID)
	headers.Set("X-Telorax-Agent-Token", c.cfg.Token)
	return headers
}

type RegisterRequest struct {
	Platform string            `json:"platform"`
	Arch     string            `json:"arch"`
	Version  string            `json:"version"`
	Capabilities TelegramCapabilities `json:"capabilities"`
}

type TelegramCapabilities struct {
	AccessibilityEnabled bool   `json:"accessibility_enabled"`
	CanObserveUI         bool   `json:"can_observe_ui"`
	CanPerformActions    bool   `json:"can_perform_actions"`
	PackageInstalled     bool   `json:"package_installed"`
	Notes                string `json:"notes,omitempty"`
}

type RegisterResponse struct {
	DeviceID string `json:"device_id"`
	Status   string `json:"status"`
}

func (c *Client) Register(ctx context.Context, req RegisterRequest) (RegisterResponse, error) {
	var out RegisterResponse
	err := c.postJSON(ctx, "/v1/mobile-agent/register", req, &out)
	return out, err
}

type HeartbeatRequest struct {
	Status       string               `json:"status"`
	Capabilities TelegramCapabilities `json:"capabilities"`
	TunnelUp     bool                 `json:"tunnel_up"`
}

type HeartbeatResponse struct {
	Status string `json:"status"`
}

func (c *Client) Heartbeat(ctx context.Context, req HeartbeatRequest) (HeartbeatResponse, error) {
	var out HeartbeatResponse
	err := c.postJSON(ctx, "/v1/mobile-agent/heartbeat", req, &out)
	return out, err
}

type AgentConfigResponse struct {
	PollIntervalSeconds int              `json:"poll_interval_seconds"`
	WireGuard           WireGuardConfig  `json:"wireguard"`
	Telegram            TelegramSettings `json:"telegram"`
}

type WireGuardConfig struct {
	Enabled        bool   `json:"enabled"`
	ConfigText     string `json:"config_text"`
	InterfaceName  string `json:"interface_name"`
	Endpoint       string `json:"endpoint"`
	ServerPublicKey string `json:"server_public_key"`
	ClientAddress  string `json:"client_address"`
}

type TelegramSettings struct {
	TargetPackage string `json:"target_package"`
	RequiresAccessibility bool `json:"requires_accessibility"`
}

func (c *Client) FetchConfig(ctx context.Context) (AgentConfigResponse, error) {
	var out AgentConfigResponse
	err := c.getJSON(ctx, "/v1/mobile-agent/config", &out)
	return out, err
}

type UpdateCheckResponse struct {
	UpdateAvailable bool   `json:"update_available"`
	Version         string `json:"version"`
	URL             string `json:"url"`
	SHA256          string `json:"sha256"`
	Mandatory       bool   `json:"mandatory"`
	ReleaseNotes    string `json:"release_notes"`
}

func (c *Client) CheckUpdate(ctx context.Context, currentVersion string) (UpdateCheckResponse, error) {
	path := fmt.Sprintf("/v1/mobile-agent/updates/check?version=%s&platform=%s&arch=%s",
		currentVersion, c.cfg.Platform, c.cfg.Arch)
	var out UpdateCheckResponse
	err := c.getJSON(ctx, path, &out)
	return out, err
}

func (c *Client) postJSON(ctx context.Context, path string, payload any, out any) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.cfg.BaseURL+path, bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header = c.headers()
	return c.do(req, out)
}

func (c *Client) getJSON(ctx context.Context, path string, out any) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.cfg.BaseURL+path, nil)
	if err != nil {
		return err
	}
	req.Header = c.headers()
	return c.do(req, out)
}

func (c *Client) do(req *http.Request, out any) error {
	resp, err := c.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	if resp.StatusCode >= 400 {
		detail := strings.TrimSpace(string(raw))
		if detail == "" {
			detail = resp.Status
		}
		return fmt.Errorf("api error %d: %s", resp.StatusCode, detail)
	}
	if out == nil || len(raw) == 0 {
		return nil
	}
	return json.Unmarshal(raw, out)
}

func (c *Client) Download(ctx context.Context, url string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("download failed: %s", resp.Status)
	}
	return io.ReadAll(resp.Body)
}
