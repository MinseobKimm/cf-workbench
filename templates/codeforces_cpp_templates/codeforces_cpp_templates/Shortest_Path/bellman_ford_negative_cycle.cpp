#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct Edge {
    int from;
    int to;
    ll weight;
};

pair<bool, vector<ll>> bellman_ford(int n, int start, const vector<Edge>& edges) {
    vector<ll> dist(n, LINF);
    dist[start] = 0;

    for (int i = 0; i < n - 1; ++i) {
        bool changed = false;

        for (const Edge& edge : edges) {
            if (dist[edge.from] == LINF) continue;
            if (dist[edge.to] <= dist[edge.from] + edge.weight) continue;
            dist[edge.to] = dist[edge.from] + edge.weight;
            changed = true;
        }

        if (!changed) break;
    }

    for (const Edge& edge : edges) {
        if (dist[edge.from] == LINF) continue;
        if (dist[edge.to] > dist[edge.from] + edge.weight) return {false, dist};
    }

    return {true, dist};
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
