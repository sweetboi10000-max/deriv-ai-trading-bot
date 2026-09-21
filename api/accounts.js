export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({
      error: "method_not_allowed"
    });
  }

  try {
    const token = req.headers.authorization
      ?.replace(/^Bearer\s+/i, "");

    if (!token) {
      return res.status(401).json({
        error: "missing_access_token"
      });
    }

    const response = await fetch(
      "https://api.derivws.com/trading/v1/options/accounts",
      {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }
    );

    const data = await response.json();

    res.setHeader("Cache-Control", "no-store");

    return res.status(response.status).json(data);

  } catch (error) {
    return res.status(500).json({
      error: "accounts_request_failed",
      message: error.message
    });
  }
}
