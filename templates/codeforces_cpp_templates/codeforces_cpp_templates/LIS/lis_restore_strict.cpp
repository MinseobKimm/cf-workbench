#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

template <class T>
vector<T> lis_restore_strict(const vector<T>& a) {
    int n = (int)a.size();
    if (n == 0) return {};

    vector<T> tail_value;
    vector<int> tail_index;
    vector<int> parent(n, -1);

    for (int i = 0; i < n; ++i) {
        int position = (int)(lower_bound(tail_value.begin(), tail_value.end(), a[i]) - tail_value.begin());

        if (position > 0) parent[i] = tail_index[position - 1];

        if (position == (int)tail_value.size()) {
            tail_value.push_back(a[i]);
            tail_index.push_back(i);
        } else {
            tail_value[position] = a[i];
            tail_index[position] = i;
        }
    }

    vector<T> result;
    for (int current = tail_index.back(); current != -1; current = parent[current]) {
        result.push_back(a[current]);
    }

    reverse(result.begin(), result.end());
    return result;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
