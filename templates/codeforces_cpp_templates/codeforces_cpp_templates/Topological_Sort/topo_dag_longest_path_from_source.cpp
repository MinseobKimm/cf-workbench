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

vector<ll> dag_longest_path_from_source(const vector<vector<pair<int, ll>>>& graph, int start) {
    auto [ok, order] = weighted_topological_sort(graph);
    int n = (int)graph.size();
    vector<ll> dp(n, -LINF);

    if (!ok) return dp;

    dp[start] = 0;
    for (int u : order) {
        if (dp[u] == -LINF) continue;
        for (auto [v, w] : graph[u]) {
            dp[v] = max(dp[v], dp[u] + w);
        }
    }

    return dp;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
