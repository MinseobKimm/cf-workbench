#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct DigitTriePrefixChecker {
    struct Node {
        array<int, 10> next;
        bool terminal;

        Node() : terminal(false) {
            next.fill(-1);
        }
    };

    vector<Node> trie;

    DigitTriePrefixChecker() {
        trie.push_back(Node());
    }

    bool insert(const string& s) {
        int node = 0;

        for (char c : s) {
            if (trie[node].terminal) return false;
            int digit = c - '0';

            if (trie[node].next[digit] == -1) {
                trie[node].next[digit] = (int)trie.size();
                trie.push_back(Node());
            }

            node = trie[node].next[digit];
        }

        if (trie[node].terminal) return false;

        for (int digit = 0; digit < 10; ++digit) {
            if (trie[node].next[digit] != -1) return false;
        }

        trie[node].terminal = true;
        return true;
    }
};

bool has_no_digit_prefix_conflict(const vector<string>& values) {
    DigitTriePrefixChecker checker;

    for (const string& value : values) {
        if (!checker.insert(value)) return false;
    }

    return true;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
