#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

vector<ll> dijkstra(const vector<vector<pair<int, ll>>>& graph, int start) {
    int n = (int)graph.size();
    vector<ll> dist(n, LINF);
    priority_queue<pair<ll, int>, vector<pair<ll, int>>, greater<pair<ll, int>>> pq;

    dist[start] = 0;
    pq.push({0, start});

    while (!pq.empty()) {
        auto [du, u] = pq.top();
        pq.pop();

        if (du != dist[u]) continue;

        for (auto [v, w] : graph[u]) {
            if (dist[v] <= du + w) continue;
            dist[v] = du + w;
            pq.push({dist[v], v});
        }
    }

    return dist;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
