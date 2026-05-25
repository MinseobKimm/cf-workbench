#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

void dfs_recursive(int u, const vector<vector<int>>& graph, vector<int>& visited, vector<int>& order) {
    visited[u] = 1;
    order.push_back(u);

    for (int v : graph[u]) {
        if (visited[v]) continue;
        dfs_recursive(v, graph, visited, order);
    }
}

vector<vector<int>> dfs_components_recursive(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<int> visited(n, 0);
    vector<vector<int>> components;

    for (int i = 0; i < n; ++i) {
        if (visited[i]) continue;
        vector<int> component;
        dfs_recursive(i, graph, visited, component);
        components.push_back(component);
    }

    return components;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
