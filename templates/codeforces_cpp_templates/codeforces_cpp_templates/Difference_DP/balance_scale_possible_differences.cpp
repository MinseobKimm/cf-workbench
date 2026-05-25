#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

vector<char> possible_weight_differences(const vector<int>& weights) {
    int total = accumulate(weights.begin(), weights.end(), 0);
    vector<char> can(total + 1, 0);
    can[0] = 1;

    for (int weight : weights) {
        vector<char> next = can;

        for (int diff = 0; diff <= total; ++diff) {
            if (!can[diff]) continue;
            if (diff + weight <= total) next[diff + weight] = 1;
            next[abs(diff - weight)] = 1;
        }

        can.swap(next);
    }

    return can;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
