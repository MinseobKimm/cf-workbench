#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct TarjanSCC {
    int n;
    int timer;
    const vector<vector<int>>& graph;
    vector<int> discovered;
    vector<int> low;
    vector<int> in_stack;
    vector<int> component_id;
    vector<vector<int>> components;
    stack<int> st;

    TarjanSCC(const vector<vector<int>>& graph)
        : n((int)graph.size()), timer(0), graph(graph), discovered(n, 0), low(n, 0), in_stack(n, 0), component_id(n, -1) {
    }

    void dfs(int u) {
        discovered[u] = low[u] = ++timer;
        st.push(u);
        in_stack[u] = 1;

        for (int v : graph[u]) {
            if (!discovered[v]) {
                dfs(v);
                low[u] = min(low[u], low[v]);
            } else if (in_stack[v]) {
                low[u] = min(low[u], discovered[v]);
            }
        }

        if (low[u] != discovered[u]) return;

        vector<int> component;
        while (true) {
            int x = st.top();
            st.pop();
            in_stack[x] = 0;
            component_id[x] = (int)components.size();
            component.push_back(x);
            if (x == u) break;
        }

        components.push_back(component);
    }

    vector<vector<int>> run() {
        for (int i = 0; i < n; ++i) {
            if (!discovered[i]) dfs(i);
        }
        return components;
    }
};


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
