import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from 'styled-components'
import { Layout } from './components/Layout'
import { GlobalStyle } from './styles/GlobalStyle'
import { theme } from './styles/theme'
import { EndpointsPage } from './pages/EndpointsPage'
import { OverviewPage } from './pages/OverviewPage'
import { PlaygroundPage } from './pages/PlaygroundPage'
import { TypesPage } from './pages/TypesPage'

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <BrowserRouter basename="/docs">
        <Layout>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/types" element={<TypesPage />} />
            <Route path="/endpoints" element={<EndpointsPage />} />
            <Route path="/playground" element={<PlaygroundPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  )
}
