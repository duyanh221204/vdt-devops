pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'nguyenduyanh221204/vdt-backend'
        CONFIG_REPO_URL = 'github.com/duyanh221204/vdt-backend-config.git'
        GITHUB_CREDENTIALS_ID = 'github-credentials'
        DOCKER_HUB_CREDENTIALS_ID = 'docker-hub-credentials'
        
        // Đường dẫn gọi lệnh docker đã cấu hình
        DOCKER_PATH = '/var/jenkins_home/docker'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                // Tự động tải source code tại thời điểm có thay đổi hoặc tag mới
                checkout scm
            }
        }

        stage('Check Git Tag') {
            steps {
                script {
                    echo "Kiểm tra tag hiện tại: ${env.GIT_BRANCH}"

                    // Nếu chuỗi lưu tên nhánh không chứa từ khóa 'tags/'
                    if (!env.GIT_BRANCH.contains('tags/')) {
                        // Lệnh error() của Jenkins sẽ lập tức in ra log và đánh dấu Pipeline là FAILURE, dừng mọi xử lý phía sau
                        error("Không phải Tag hợp lệ")
                    }

                    // Lấy ra tên tag (ví dụ: v1.0.0) từ chuỗi env.GIT_BRANCH
                    // Biến env.GIT_BRANCH của Jenkins có định dạng 'refs/tags/v1.0.0'
                    // Hàm split('/')[-1] dùng để cắt chuỗi, chỉ lấy phần chữ 'v1.0.0'
                    // Gán vào env.IMAGE_TAG để tái sử dụng ở các stage sau
                    env.IMAGE_TAG = env.GIT_BRANCH.split('/')[-1]
                    echo "Tag mới nhận được: ${env.IMAGE_TAG}"

                    // Kiểm tra định dạng vX.Y.Z
                    // Quy tắc: Bắt đầu bằng chữ 'v', theo sau là 3 nhóm số cách nhau bởi dấu chấm
                    def tagRegex = /^v\d+\.\d+\.\d+$/
                    if (!(env.IMAGE_TAG ==~ tagRegex)) {
                        error("Định dạng Tag '${env.IMAGE_TAG}' không hợp lệ")
                    }
                    echo "Định dạng Tag hợp lệ: ${env.IMAGE_TAG}"

                    // So sánh tag mới với tag hiện tại trong file values.yaml của config repo
                    // Gọi phương thức withCredentials để lấy credentials từ Jenkins một cách an toàn
                    withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDENTIALS_ID}", passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                        // Clone config repo một lần, tái sử dụng ở stage Update Config Repo
                        sh "rm -rf config-repo && git clone https://\${GIT_USERNAME}:\${GIT_PASSWORD}@${CONFIG_REPO_URL} config-repo"

                        // Tìm chuỗi tag cũ trong file values.yaml bằng Regex
                        def valuesContent = readFile 'config-repo/values.yaml'
                        def matcher = valuesContent =~ /tag:\s*([^\s]+)/

                        if (matcher.find()) {
                            def currentTag = matcher.group(1)
                            matcher = null // Giải phóng bộ nhớ của matcher
                            echo "Tag hiện tại đang chạy trên hệ thống: ${currentTag}"

                            // Sử dụng lệnh 'sort -V' của Linux để so sánh 2 chuỗi phiên bản số
                            def result = sh(
                                script: """
                                # Nếu tag mới trùng khít tag cũ
                                if [ "${env.IMAGE_TAG}" = "${currentTag}" ]; then exit 1; fi
                                # Sắp xếp phiên bản, nếu tag cũ đứng sau tag mới nghĩa là tag mới nhỏ hơn tag cũ
                                lowest=\$(printf "${env.IMAGE_TAG}\n${currentTag}" | sort -V | head -n1)
                                if [ "\$lowest" = "${env.IMAGE_TAG}" ]; then exit 1; fi
                                """,
                                returnStatus: true
                            )

                            if (result != 0) {
                                error("Phiên bản tag mới (${env.IMAGE_TAG}) phải lớn hơn phiên bản hiện tại (${currentTag})")
                            } else {
                                echo "Tag mới (${env.IMAGE_TAG}) lớn hơn tag hiện tại (${currentTag}), tiếp tục pipeline"
                            }
                        } else {
                            echo "Không tìm thấy tag cũ trong values.yaml"
                        }
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Lấy tag của Git làm tag cho Docker Image - dùng env.IMAGE_TAG đã xác định ở stage trước
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDENTIALS_ID}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh """
                        echo "Đăng nhập hệ thống Docker Hub"
                        echo "\$DOCKER_PASSWORD" | ${DOCKER_PATH} login -u "\$DOCKER_USERNAME" --password-stdin

                        echo "Tiến hành build Image với tag: ${env.IMAGE_TAG}"
                        ${DOCKER_PATH} build -t ${DOCKER_IMAGE}:${env.IMAGE_TAG} .

                        echo "Tiến hành đẩy Image lên Docker Hub"
                        ${DOCKER_PATH} push ${DOCKER_IMAGE}:${env.IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Update Config Repo') {
            steps {
                script {
                    // Tái sử dụng config-repo đã clone ở stage Check Git Tag, không cần clone lại
                    withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDENTIALS_ID}", passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                        sh """
                        cd config-repo

                        echo "Cấu hình thông tin user Git"
                        git config user.email "devops@vdt2026.com" && git config user.name "Jenkins CI"

                        echo "Cập nhật dữ liệu mới nhất từ GitHub để tránh xung đột dữ liệu"
                        git pull origin main --rebase

                        echo "Chỉnh sửa version tag trong tệp values.yaml"
                        # Cú pháp sed -i dùng để sửa trực tiếp tệp
                        # 's/chuỗi_cũ/chuỗi_mới/g' sẽ tìm thuộc tính 'tag: ' và ghi đè tag mới vào sau nó
                        sed -i "s/tag: .*/tag: ${env.IMAGE_TAG}/g" values.yaml

                        # Kiểm tra thay đổi
                        # Lệnh 'git diff --quiet' sẽ kiểm tra xem có dòng code nào bị thay đổi không
                        if git diff --quiet values.yaml; then
                            echo "Phiên bản tag '${env.IMAGE_TAG}' đã tồn tại trong cấu hình hiện tại"
                            echo "Từ chối cập nhật"
                            # Dừng pipeline với trạng thái FAILURE
                            exit 1
                        else
                            echo "Phát hiện tag mới, commit và push thay đổi lên GitHub"
                            git add values.yaml
                            git commit -m "Update image tag to ${env.IMAGE_TAG} via Jenkins Pipeline"
                            git push https://\${GIT_USERNAME}:\${GIT_PASSWORD}@${CONFIG_REPO_URL} main
                        fi
                        """
                    }
                }
            }
        }
    }

    // Xử lý sau khi pipeline kết thúc
    post {
        always {
            // Dọn dẹp workspace sau khi pipeline kết thúc
            cleanWs()
        }
        success {
            // Ghi log xác nhận pipeline đã chạy thành công
            echo 'Pipeline thành công'
        }
        failure {
            // Log lỗi
            echo 'Pipeline thất bại. Cần kiểm tra log chi tiết ở các stage trên'
        }
    }
}