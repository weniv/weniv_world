import os

# 난독화하려는 폴더 설정
target_directory = "./assets./py"

# 폴더 내의 모든 파일을 검색
for filename in os.listdir(target_directory):
    # .py 파일만 대상으로 함
    if filename.endswith(".py"):
        # 원본 파일의 절대 경로
        source_path = os.path.join(target_directory, filename)

        # 출력 파일의 절대 경로
        output_path = os.path.join("dist/assets/py", filename)

        if not os.path.exists("dist/assets/py"):
            os.makedirs("dist/assets/py")

        # pyminifier를 사용하여 난독화
        os.system(
            f"pyminifier --obfuscate-builtins -O --outfile={output_path} {source_path}"
        )

print("난독화가 완료되었습니다.")
