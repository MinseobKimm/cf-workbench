#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

pair<bool, vector<int>> weighted_topological_sort(const vector<vector<pair<int, ll>>>& graph) {
    int n = (int)graph.size();
    vector<int> indegree(n, 0);

    for (int u = 0; u < n; ++u) {
        for (auto [v, w] : graph[u]) ++indegree[v];
    }

    queue<int> q;
    for (int i = 0; i < n; ++i) {
        if (indegree[i] == 0) q.push(i);
    }

    vector<int> order;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        order.push_back(u);

        for (auto [v, w] : graph[u]) {
            --indegree[v];
            if (indegree[v] == 0) q.push(v);
        }
    }

    return {(int)order.size() == n, order};
}

pair<ll, ll> dag_longest_path_and_critical_edge_count(const vector<vector<pair<int, ll>>>& graph, int start, int target) {
    auto [ok, order] = weighted_topological_sort(graph);
    int n = (int)graph.size();
    vector<ll> dist(n, -LINF);
    vector<vector<pair<int, ll>>> reverse_graph(n);

    for (int u = 0; u < n; ++u) {
        for (auto [v, w] : graph[u]) {
            reverse_graph[v].push_back({u, w});
        }
    }

    if (!ok) return {-LINF, 0};

    dist[start] = 0;
    for (int u : order) {
        if (dist[u] == -LINF) continue;
        for (auto [v, w] : graph[u]) {
            dist[v] = max(dist[v], dist[u] + w);
        }
    }

    if (dist[target] == -LINF) return {-LINF, 0};

    ll count = 0;
    vector<int> seen(n, 0);
    queue<int> q;
    q.push(target);
    seen[target] = 1;

    while (!q.empty()) {
        int v = q.front();
        q.pop();

        for (auto [u, w] : reverse_graph[v]) {
            if (dist[u] == -LINF) continue;
            if (dist[u] + w != dist[v]) continue;
            ++count;
            if (!seen[u]) {
                seen[u] = 1;
                q.push(u);
            }
        }
    }

    return {dist[target], count};
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
