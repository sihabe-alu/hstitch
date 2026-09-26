# hstitch — 사진 가로 이어붙이기 웹UI

## 목적
개인용. mac mini에서 서버를 실행하고, Windows PC가 tailscale로 접속해 브라우저에서 사진 2~3장을 가로로 이어붙인다. 원본 해상도·화질 유지, 가벼움 우선. Windows 설치형 배포는 불필요(브라우저만 사용).

## 요구사항
- 사진 2~3장 업로드(파일 선택 / 드래그앤드롭), 순서 변경.
- 리사이즈 없음. 캔버스 너비 = 각 너비의 합, 높이 = 최대 높이.
- 높이가 작은 사진은 세로 중앙 정렬, 여백은 흰색.
- 출력 포맷 선택: PNG(기본) / JPEG.
- 미리보기 후 다운로드.

## 비목표
인증, 서버 저장, 색/정렬 옵션 UI, 세로 이어붙이기, 리사이즈/크롭, 4장 이상 제한 검증.

## 조사 결과 요약
gh 검색상 웹UI + 초경량 + 무손실 + Windows release를 모두 만족하는 기존 repo 없음. 최근접 참고: 00xJS/I-Combinator(단일 HTML, canvas 방식, 라이선스 없음). canvas 방식은 브라우저 크기 한계(~16k px)와 JPEG 재인코딩 문제가 있어 서버 측 Pillow 처리를 택함.

## 구조
위치: `~/hstitch/` (ComfyUI repo 밖)

| 파일 | 역할 |
|---|---|
| `app.py` | Flask. `GET /` → `index.html`, `POST /stitch` → 합성 이미지 반환 |
| `index.html` | 단일 파일 프론트: 업로드, 썸네일 순서 변경, 포맷 선택, 미리보기, 다운로드 |
| `requirements.txt` | `flask`, `pillow` |
| `run.sh` | tailscale IP에 바인딩해 서버 실행 |
| `tests/test_stitch.py` | pytest |

## 합성 로직 (`POST /stitch`)
입력: multipart 이미지 파일들(업로드 순서 유지) + `format` (`png` | `jpeg`, 기본 `png`).

1. 각 파일을 Pillow로 열고 `ImageOps.exif_transpose` 적용(폰 사진 회전 정규화. 픽셀 수는 불변).
2. 캔버스 생성: `(sum(w), max(h))`, 흰색 배경. 각 이미지를 `y = (H - h) // 2` 위치에 붙임. RGBA는 알파를 흰 배경 위에 합성.
3. 저장:
   - PNG: 그대로.
   - JPEG: `quality=100, subsampling=0`.
   - 첫 이미지의 ICC 프로파일 유지.
4. 바이너리 응답(`image/png` | `image/jpeg`). 프론트가 blob URL로 미리보기·다운로드.

이미지 개수 검증 없음: 1장이면 그대로 반환, 4장 이상도 합침. 디코드 실패만 400.

## 운영
- 인증 없음. 바인딩 주소는 tailscale IP(`tailscale ip -4`)로 제한해 LAN 노출 방지.
- 메모리 내 처리, 서버에 저장하지 않음.

## 테스트
- 높이가 다른 두 이미지 합성 시 크기 == `(w1+w2, max(h1,h2))`.
- PNG 왕복 후 각 원본 영역 픽셀이 입력과 동일(무손실).
- 깨진 파일 업로드 시 400.
