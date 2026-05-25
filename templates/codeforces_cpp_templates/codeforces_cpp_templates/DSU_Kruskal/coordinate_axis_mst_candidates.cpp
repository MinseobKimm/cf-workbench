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

struct Point3D {
    ll x;
    ll y;
    ll z;
};

struct Node3D {
    ll x;
    ll y;
    ll z;
    int id;
};

struct Edge {
    int from;
    int to;
    ll weight;
};

ll coordinate_cost(const Node3D& a, const Node3D& b) {
    return min({llabs(a.x - b.x), llabs(a.y - b.y), llabs(a.z - b.z)});
}

vector<Edge> coordinate_axis_candidates(const vector<Point3D>& points) {
    int n = (int)points.size();
    vector<Node3D> nodes(n);

    for (int i = 0; i < n; ++i) {
        nodes[i] = {points[i].x, points[i].y, points[i].z, i};
    }

    vector<Edge> edges;

    auto add_by = [&](auto getter) {
        sort(nodes.begin(), nodes.end(), [&](const Node3D& a, const Node3D& b) {
            return getter(a) < getter(b);
        });

        for (int i = 1; i < n; ++i) {
            edges.push_back({nodes[i - 1].id, nodes[i].id, coordinate_cost(nodes[i - 1], nodes[i])});
        }
    };

    add_by([](const Node3D& p) { return p.x; });
    add_by([](const Node3D& p) { return p.y; });
    add_by([](const Node3D& p) { return p.z; });

    return edges;
}

ll coordinate_axis_mst(const vector<Point3D>& points) {
    int n = (int)points.size();
    vector<Edge> edges = coordinate_axis_candidates(points);

    sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        return a.weight < b.weight;
    });

    DSU dsu(n);
    ll total = 0;
    int used = 0;

    for (const Edge& edge : edges) {
        if (!dsu.unite(edge.from, edge.to)) continue;
        total += edge.weight;
        ++used;
        if (used == n - 1) break;
    }

    return used == n - 1 ? total : LINF;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
