package tunnel

import (
	"fmt"
	"strings"

	"github.com/LordDeveloper/telorax/android-agent/internal/api"
)

type Manager struct {
	lastConfig string
	active     bool
}

func NewManager() *Manager {
	return &Manager{}
}

func (m *Manager) Apply(cfg api.WireGuardConfig) (string, error) {
	if !cfg.Enabled {
		m.active = false
		m.lastConfig = ""
		return "wireguard disabled by server", nil
	}
	text := strings.TrimSpace(cfg.ConfigText)
	if text == "" {
		text = BuildClientConfig(cfg)
	}
	if err := validateConfig(text); err != nil {
		return "", err
	}
	m.lastConfig = text
	m.active = true
	return text, nil
}

func (m *Manager) Active() bool { return m.active }

func (m *Manager) LastConfig() string { return m.lastConfig }

func BuildClientConfig(cfg api.WireGuardConfig) string {
	if strings.TrimSpace(cfg.ClientAddress) == "" || strings.TrimSpace(cfg.ServerPublicKey) == "" {
		return ""
	}
	privateKey := "[CLIENT_PRIVATE_KEY]"
	if strings.Contains(cfg.ConfigText, "PrivateKey") {
		return cfg.ConfigText
	}
	lines := []string{
		"[Interface]",
		"PrivateKey = " + privateKey,
		"Address = " + cfg.ClientAddress,
		"DNS = 1.1.1.1",
		"",
		"[Peer]",
		"PublicKey = " + cfg.ServerPublicKey,
		"AllowedIPs = 0.0.0.0/0, ::/0",
	}
	if endpoint := strings.TrimSpace(cfg.Endpoint); endpoint != "" {
		lines = append(lines, "Endpoint = "+endpoint)
	}
	lines = append(lines, "PersistentKeepalive = 25")
	return strings.Join(lines, "\n")
}

func validateConfig(text string) error {
	if !strings.Contains(text, "[Interface]") || !strings.Contains(text, "[Peer]") {
		return fmt.Errorf("invalid wireguard config")
	}
	return nil
}
