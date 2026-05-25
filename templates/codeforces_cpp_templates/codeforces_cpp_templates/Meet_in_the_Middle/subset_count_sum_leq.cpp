#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

void make_subset_sums(const vector<ll>& a, int left, int right, ll sum, vector<ll>& output) {
    if (left == right) {
        output.push_back(sum);
        return;
    }

    make_subset_sums(a, left + 1, right, sum, output);
    make_subset_sums(a, left + 1, right, sum + a[left], output);
}

ll count_subset_sum_leq(const vector<ll>& a, ll limit) {
    int n = (int)a.size();
    vector<ll> left_sums;
    vector<ll> right_sums;

    make_subset_sums(a, 0, n / 2, 0, left_sums);
    make_subset_sums(a, n / 2, n, 0, right_sums);
    sort(right_sums.begin(), right_sums.end());

    ll count = 0;
    for (ll x : left_sums) {
        count += upper_bound(right_sums.begin(), right_sums.end(), limit - x) - right_sums.begin();
    }

    return count;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
