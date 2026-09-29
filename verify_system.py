import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def verify_system():
    print("--- 1. Testing Frontend HTML ---")
    with urllib.request.urlopen("http://127.0.0.1:5173") as res:
        html = res.read().decode('utf-8')
        assert '<div id="root">' in html
        print("Frontend HTML serving OK! Status:", res.status)

    print("\n--- 2. Testing Backend Health ---")
    with urllib.request.urlopen("http://127.0.0.1:8000/health") as res:
        health = json.loads(res.read().decode())
        print("Health status:", health)
        assert health["status"] == "healthy"

    print("\n--- 3. Testing Guest Recommendations ---")
    with urllib.request.urlopen("http://127.0.0.1:8000/api/recommendations?limit=3") as res:
        rec = json.loads(res.read().decode())
        print("Algorithm:", rec["algorithm"])
        print("Cached:", rec["cached"])
        print("Execution Time:", rec["execution_time_ms"], "ms")
        for r in rec["recommendations"]:
            print(f"  - [{r['item']['cloud_provider']}] {r['item']['name']} ({r['score']*100:.0f}% Match) -> Reason: {r['reason']}")

    print("\n--- 4. Testing User Login ---")
    login_data = json.dumps({"email": "admin@cloudrec.io", "password": "Admin@123"}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        auth = json.loads(res.read().decode())
        token = auth["access_token"]
        print("Logged in as:", auth["user"]["name"], "| Role:", auth["user"]["role"])

    print("\n--- 5. Testing Personalized Recommendations (Elena AI Persona) ---")
    login_elena = json.dumps({"email": "elena.ai@cloudrec.io", "password": "Password@123"}).encode()
    req_elena = urllib.request.Request(
        "http://127.0.0.1:8000/api/auth/login",
        data=login_elena,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_elena) as res:
        elena_token = json.loads(res.read().decode())["access_token"]

    rec_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/recommendations?limit=4",
        headers={"Authorization": f"Bearer {elena_token}"}
    )
    with urllib.request.urlopen(rec_req) as res:
        elena_recs = json.loads(res.read().decode())
        print("Elena Recs Algorithm:", elena_recs["algorithm"])
        for r in elena_recs["recommendations"]:
            print(f"  - {r['item']['name']} ({r['score']*100:.0f}% Match) -> Reason: {r['reason']}")

    print("\n--- 6. Testing Similar Items API for Item #1 ---")
    with urllib.request.urlopen("http://127.0.0.1:8000/api/recommendations/similar/1?limit=3") as res:
        sim = json.loads(res.read().decode())
        for r in sim["recommendations"]:
            print(f"  - Similar to Item #1: {r['item']['name']} ({r['score']}) -> Reason: {r['reason']}")

    print("\n--- 7. Testing Admin Analytics ---")
    admin_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(admin_req) as res:
        stats = json.loads(res.read().decode())
        print(f"Admin KPIs: Users={stats['total_users']}, Items={stats['total_items']}, Interactions={stats['total_interactions']}, AvgRating={stats['average_rating']}★")
        print(f"Interaction Breakdown: {stats['interaction_types_breakdown']}")

    print("\n==========================================")
    print("SUCCESS: ALL FULL-STACK SYSTEMS VALIDATED!")
    print("==========================================")

if __name__ == "__main__":
    verify_system()
