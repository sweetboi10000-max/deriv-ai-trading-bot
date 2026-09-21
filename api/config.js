export default function handler(req, res) {
  const clientId = process.env.DERIV_CLIENT_ID || "";
  const redirectUri = process.env.DERIV_REDIRECT_URI || "";
  const scope = process.env.DERIV_SCOPE || "trade";

  res.setHeader("Cache-Control", "no-store");

  return res.status(200).json({
    configured: Boolean(clientId && redirectUri),
    clientId,
    redirectUri,
    scope
  });
}
