# Troubleshooting

## Competitive Companion payload가 안 들어올 때

- `cfw doctor`를 실행합니다.
- 서버 주소가 `http://127.0.0.1:27121`인지 확인합니다.
- Competitive Companion custom port에 `27121`을 추가합니다.
- Windows 방화벽 프롬프트가 떠 있으면 localhost 접근을 허용합니다.
- 필요하면 `10045`, `10043` 같은 다른 Competitive Companion 기본 포트를 시험합니다.

## 컴파일러 문제

Windows에서는 `C:\msys64\ucrt64\bin\g++.exe`를 권장합니다.

```bash
cfw doctor
```

`C:\mingw64\bin\g++.exe` 또는 GCC 8.1.0이 먼저 잡히면 C++17과 `#include <bits/stdc++.h>`에서 깨질 수 있습니다. 이 프로젝트는 UCRT64가 설치되어 있으면 해당 compiler를 우선 사용하고, 실행 중 PATH 앞에도 UCRT64 bin을 붙입니다.

## 샘플이 WA일 때

`.cfw/runs/latest.log`를 확인합니다. 기본 비교 모드는 `tokens`입니다.

```bash
cfw test 954G --compare trim
cfw test 954G --compare exact
```

## 제출 페이지가 열리지 않을 때

`cfw submit 954G --open-browser`는 로컬 테스트가 모두 AC여야 진행합니다. 확인 문구는 정확히 다음처럼 입력해야 합니다.

```text
SUBMIT 954G
```

이 도구는 Codeforces에 직접 HTTP 제출을 하지 않습니다.
