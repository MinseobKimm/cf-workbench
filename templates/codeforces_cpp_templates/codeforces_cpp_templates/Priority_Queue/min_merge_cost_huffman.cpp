#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll min_merge_cost_huffman(vector<ll> values) {
    priority_queue<ll, vector<ll>, greater<ll>> pq(values.begin(), values.end());
    ll answer = 0;

    while (pq.size() > 1) {
        ll a = pq.top();
        pq.pop();
        ll b = pq.top();
        pq.pop();
        answer += a + b;
        pq.push(a + b);
    }

    return answer;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
