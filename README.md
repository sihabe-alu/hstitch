# hstitch

사진 2~3장을 가로로 이어 붙여 한 장으로 만들어 주는 작은 Flask 웹앱.

## 접속 주소

서버는 Tailscale IP에만 바인딩된다 (`run.sh` 참고). 같은 tailnet(`sihabe@`)에 로그인된 기기에서만 접속 가능하고, 공용 인터넷이나 같은 공유기(LAN)에서는 열리지 않는다.

| 방식 | 주소 |
|------|------|
| Tailscale IP | http://100.105.168.12:5050 |
| MagicDNS | http://sialu-macmini.tail2086ee.ts.net:5050 |

- 접속하는 기기(폰, 다른 PC 등)에 Tailscale 앱을 설치하고 같은 계정으로 로그인해야 한다.
- 서버가 실행 중이어야 한다 (아래 실행 방법 참고).
- Tailscale IP는 기기에 고정 할당되지만, 바뀌었다면 `tailscale ip -4`로 확인한다.

## 실행

```sh
./run.sh
```

`.venv`를 활성화하고 `tailscale ip -4`로 얻은 주소의 5050 포트에서 Flask를 띄운다. 처음이라면 먼저 의존성을 설치한다.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

포트를 5050으로 쓰는 이유는 macOS AirPlay 수신이 5000을 점유하기 때문.

## 사용법

1. 브라우저에서 접속 주소를 연다.
2. 사진을 끌어놓거나 클릭해서 선택한다.
3. 출력 형식(PNG 무손실 / JPEG)과 "높이 맞춤"(작은 사진 확대) 옵션을 고른다.
4. 이어 붙인 결과 이미지를 받는다.

## API

`POST /stitch` (multipart/form-data)

| 필드 | 설명 |
|------|------|
| `images` | 이어 붙일 이미지 파일들 (순서대로 왼쪽 → 오른쪽) |
| `format` | `png`(기본) 또는 `jpeg` |
| `fit` | `1`이면 가장 큰 높이에 맞춰 작은 사진을 확대 |

성공하면 `image/png` 또는 `image/jpeg`를 돌려주고, 이미지가 없거나 손상된 파일이면 `400`을 돌려준다.

```sh
curl -F images=@a.jpg -F images=@b.jpg -F format=png \
  http://100.105.168.12:5050/stitch -o out.png
```

## 테스트

```sh
.venv/bin/pytest
```
