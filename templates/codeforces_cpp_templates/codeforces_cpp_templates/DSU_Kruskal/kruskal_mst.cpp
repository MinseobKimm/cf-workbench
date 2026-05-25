#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct DSU {
    vector<int> parent;
    vector<int> size;

    DSU(int n = 0) {
        init(n);
    }

    void init(int n) {
        parent.resize(n);
        size.assign(n, 1);
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        if (parent[x] == x) return x;
        return parent[x] = find(parent[x]);
    }

    bool unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) return false;
        if (size[a] < size[b]) swap(a, b);
        parent[b] = a;
        size[a] += size[b];
        return true;
    }
};

struct Edge {
    int from;
    int to;
    ll weight;
};

pair<ll, vector<Edge>> kruskal_mst(int n, vector<Edge> edges) {
    sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        return a.weight < b.weight;
    });

    DSU dsu(n);
    ll total = 0;
    vector<Edge> chosen;

    for (const Edge& edge : edges) {
        if (!dsu.unite(edge.from, edge.to)) continue;
        total += edge.weight;
        chosen.push_back(edge);
        if ((int)chosen.size() == n - 1) break;
    }

    if ((int)chosen.size() != n - 1) return {LINF, {}};
    return {total, chosen};
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
