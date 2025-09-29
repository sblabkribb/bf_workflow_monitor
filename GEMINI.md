## `labnote` 폴더 구조 및 데이터 명세서

### 1\. 개요

이 문서는 `vscode-labnote-extension`에 의해 생성되는 **`labnote` 폴더의 표준 구조와 내부 파일의 데이터 형식**을 정의합니다. 이 명세는 `bf_workflow_monitor`가 실험 데이터를 정확하게 파싱하여 워크플로우 진행 상태, 자동화 수준, 성능 지표(KPI)를 시각화하기 위한 기술적 기준을 제공합니다.

### 2\. `labnote` 폴더 표준 구조

`vscode-labnote-extension`은 "Create Labnote" 명령 실행 시 다음과 같은 계층 구조를 가진 폴더를 생성합니다.

```
001_Cloning_pGET-CBA_Vector/       <- 최상위 실험 폴더 (프로젝트 단위)
├── README.md                      <- 실험 개요 및 워크플로우 진행 상태
│
├── 001_WB030_DNA_Assembly.md      <- 1번 워크플로우 파일
├── 002_WT010_Transformation.md    <- 2번 워크플로우 파일
│   ...
│
├── images/                        <- 이미지 리소스 폴더
│   ├── result_01.png
│   └── setup_diagram.jpg
│
└── resources/                     <- 기타 리소스 폴더 (e.g., 프로토콜, 데이터 파일)
    └── transformation_protocol.pdf
```

### 3\. 핵심 파일 상세 명세

#### 3.1. `README.md` : 실험 개요 및 마스터 트래커

실험 전체의 개요와 모든 워크플로우의 진행 상태를 한눈에 볼 수 있는 마스터 파일입니다.

  * **파일 예시 (`README.md`)**:

    ```markdown
    ---
    title: "Cloning of pGET-CBA Vector"
    author: "Gildong Hong"
    status: "In Progress"
    created_date: "2025-09-29"
    ---

    # 001. Cloning of pGET-CBA Vector

    ## 1. Overview
    pGET-CBA 벡터 클로닝을 위한 전체 실험 과정입니다.

    ## 2. Workflows Status
    - [x] [001_WB030_DNA_Assembly.md](./001_WB030_DNA_Assembly.md)
    - [ ] [002_WT010_Transformation.md](./002_WT010_Transformation.md)
    ```

  * **파싱 데이터**:

      * **YAML Front Matter**:
          * `title`: 실험 제목
          * `author`: 실험 생성자
          * `status`: 실험의 전체 상태 (`Planned`, `In Progress`, `Completed`, `On Hold`). 이 값은 `Workflows Status`를 통해 자동 계산될 수 있습니다.
          * `created_date`: 생성 일자
      * **Workflows Status**:
          * 체크박스 `[x]`는 해당 워크플로우가 **완료(Completed)** 되었음을 의미합니다.
          * `[ ]`는 **미완료** 상태이며, 내부 Unit Operation들의 상태에 따라 **진행 중(In Progress)** 또는 **계획됨(Planned)** 으로 세분화됩니다.

-----

#### 3.2. 워크플로우 파일 (`*.md`) : Unit Operation의 집합

각 워크플로우는 여러 개의 Unit Operation(UO)으로 구성되며, 실제 실험 내용이 기록되는 파일입니다.

  * **파일 예시 (`001_WB030_DNA_Assembly.md`)**:

    ```markdown
    ---
    title: "WB030 - DNA Assembly"
    experimenter: "Gildong Hong"
    status: "Completed"
    created_date: "2025-09-29"
    last_updated_date: "2025-09-29"
    ---

    # WB030 - DNA Assembly

    ### [UHW010 PCR]
    #### Meta
    - **Experimenter**: Gildong Hong
    - **Start_date**: 2025-09-29
    - **End_date**: 2025-09-29

    #### Automation
    - **HW**: UHW010 (Thermal Cycler)
    - **SW**: USW020 (PCR Protocol Designer)

    #### KPI
    - **성공률 (%)**: 98.5
    - **소요 시간 (분)**: 90

    #### Results & Discussions
    PCR 증폭 산물을 전기영동으로 확인함. (images/pcr_result.png)

    ---

    ### [UHW400 Manual Ligation]
    #### Meta
    - **Experimenter**: Cheolsu Kim
    - **Start_date**: 2025-09-30
    - **End_date**:

    #### Automation
    - **HW**: UHW400 (Manual Pipetting)
    - **SW**: None

    #### KPI
    - **소요 시간 (분)**: 30

    #### Results & Discussions
    (여기에 결과가 기록되면 '완료' 상태가 됩니다)
    ```

  * **파싱 데이터**:

      * **YAML Front Matter**: 워크플로우 기본 정보
          * `status`: 워크플로우의 상태. 내부 모든 UO가 '완료'일 때 'Completed'가 됩니다.
      * **Unit Operation (UO) 블록**: `###` 헤더로 각 UO를 구분합니다.
          * **ID 및 이름**: `### [UHW010 PCR]`에서 `UHW010`과 `PCR`을 추출합니다.
          * **`Meta` 섹션**:
              * `Start_date`, `End_date`를 통해 UO의 **기간**을 파악합니다.
              * **상태 판별 로직**:
                  * **완료 (Completed)**: `End_date`가 있고, `Results & Discussions` 섹션에 내용이 존재.
                  * **진행 중 (In Progress)**: `Start_date`는 있으나 `End_date`가 비어 있음.
                  * **계획됨 (Planned)**: `Start_date`가 비어 있거나 미래 날짜.
          * **`Automation` 섹션**:
              * `HW`, `SW` 목록을 추출하여 **자동화 수준(Automation Level)**을 계산합니다.
              * **계산 로직 예시**:
                  * `Manual` 키워드가 포함된 경우: 0점
                  * `HW`만 있는 경우: 1점
                  * `SW`만 있는 경우: 2점
                  * `HW`와 `SW`가 모두 있는 경우: 3점
                  * `None`: 0점
          * **`KPI` 섹션**:
              * Key-Value 쌍으로 정의된 **성능 지표**를 추출합니다. Key는 지표명, Value는 값과 단위를 포함할 수 있습니다.
              * 예: `성공률 (%)`, `소요 시간 (분)`
          * **`Results & Discussions` 섹션**:
              * 내용의 **존재 유무**는 `End_date`와 함께 UO의 **완료 여부**를 최종 판단하는 중요한 기준입니다.

### 4\. `bf_workflow_monitor` 연동 방안

`bf_workflow_monitor`는 상기 명세에 따라 `labnote` 폴더 내 마크다운 파일들을 주기적으로 파싱하여 다음 정보를 추출하고 데이터베이스에 저장합니다.

1.  **실험 목록**: 최상위 폴더 이름과 `README.md`의 `title`을 조합하여 생성합니다.
2.  **워크플로우 구조**: `README.md`의 워크플로우 목록과 각 워크플로우 파일(`*.md`) 내 UO 목록을 파싱하여 **실험-워크플로우-Unit Operation**의 계층 구조를 완성합니다.
3.  **상태 및 지표 추출**:
    *   **UO 상태**: 각 UO 블록에서 `Meta`와 `Results` 정보를 조합하여 상태(계획/진행/완료)를 판별합니다.
    *   **워크플로우/실험 상태**: 하위 요소들의 상태를 집계하여 상위 레벨의 상태(`In Progress`, `Completed` 등)를 결정합니다.
    *   **자동화 수준**: `Automation` 섹션의 명세에 따라 UO별, 워크플로우별, 실험 전체의 자동화 점수를 계산합니다.
    *   **KPI 집계**: `KPI` 섹션에서 성능 지표를 추출하여 UO별 성능을 추적하고, 전체 실험의 평균 또는 총합을 계산합니다.

이러한 정형화된 데이터 구조를 통해 `워크플로개발체계.jpg`에서 구상하는 타임라인 기반의 시각화와 정량적 분석(예: 자동화 수준 추이, 단계별 소요 시간 분석)이 가능해집니다.