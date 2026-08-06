import json
with open("/etc/v2ray-agent/xray/config.json") as f:
    d = json.load(f)
if "policy" not in d:
    d["policy"] = {}
d["policy"]["system"] = {"statsOutboundUplink": True, "statsOutboundDownlink": True}
with open("/etc/v2ray-agent/xray/config.json", "w") as f:
    json.dump(d, f, indent=2)
print("policy fixed")
