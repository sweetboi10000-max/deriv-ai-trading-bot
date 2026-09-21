export default async function handler(req, res) {
  try {
    const response = await fetch(
      "https://api.derivws.com/v1/health",
      {
        cache: "no-store"
      }
    );

    const data = await response.json();

    return res
      .status(response.ok ? 200 : response.status)
      .json(data);

  } catch (error) {
    return res.status(503).json({
      ok: false,
      error: error.message
    });
  }
}
