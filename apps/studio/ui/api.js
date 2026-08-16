import { setSave } from "./state.js";

export async function api(path, method, body) {
  const opts = method === "GET"
    ? undefined
    : { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

export function saveFailed(err) {
  console.error(err);
  setSave("save failed — is the server up?");
}
