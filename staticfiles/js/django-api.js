/**
 * Django API와 연동하는 JavaScript 모듈
 */

class DjangoGameAPI {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.currentStoryId = null;
        this.csrfToken = window.CSRF_TOKEN || '';
        this.apiUrls = window.API_URLS || {};
    }

    /**
     * 고유한 세션 ID 생성
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * API 요청을 위한 기본 설정
     */
    getRequestConfig(method = 'POST', data = null) {
        const config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            }
        };

        if (data && method !== 'GET') {
            config.body = JSON.stringify(data);
        }

        return config;
    }

    /**
     * Python 코드 실행
     */
    async executeCode(code, storyId = null) {
        try {
            const response = await fetch(this.apiUrls.execute_code || '/api/execute-code/', 
                this.getRequestConfig('POST', {
                    code: code,
                    session_id: this.sessionId,
                    story_id: storyId || this.currentStoryId
                })
            );

            const result = await response.json();
            
            if (result.success) {
                // 게임 상태 업데이트 이벤트 발생
                this.dispatchGameStateUpdate(result);
            }

            return result;
        } catch (error) {
            console.error('Error executing code:', error);
            return {
                success: false,
                error: 'Network error: ' + error.message
            };
        }
    }

    /**
     * 게임 세션 저장
     */
    async saveSession(worldData = {}, characterData = {}, submittedCode = '') {
        try {
            const response = await fetch(this.apiUrls.save_session || '/api/save-session/',
                this.getRequestConfig('POST', {
                    session_id: this.sessionId,
                    story_id: this.currentStoryId,
                    world_data: worldData,
                    character_data: characterData,
                    submitted_code: submittedCode
                })
            );

            return await response.json();
        } catch (error) {
            console.error('Error saving session:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 게임 세션 로드
     */
    async loadSession(storyId = null) {
        try {
            const response = await fetch(this.apiUrls.load_session || '/api/load-session/',
                this.getRequestConfig('POST', {
                    session_id: this.sessionId,
                    story_id: storyId || this.currentStoryId
                })
            );

            const result = await response.json();
            
            if (result.success) {
                // 게임 상태 업데이트 이벤트 발생
                this.dispatchGameStateUpdate(result);
            }

            return result;
        } catch (error) {
            console.error('Error loading session:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 새 게임 세션 생성
     */
    async createSession(storyId = null) {
        try {
            const response = await fetch(this.apiUrls.create_session || '/api/create-session/',
                this.getRequestConfig('POST', {
                    story_id: storyId
                })
            );

            const result = await response.json();
            
            if (result.success) {
                this.sessionId = result.session_id;
                this.currentStoryId = storyId;
                
                // 게임 상태 업데이트 이벤트 발생
                this.dispatchGameStateUpdate(result);
            }

            return result;
        } catch (error) {
            console.error('Error creating session:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 스토리 목록 가져오기
     */
    async getStories() {
        try {
            const response = await fetch('/api/stories/', 
                this.getRequestConfig('GET')
            );

            return await response.json();
        } catch (error) {
            console.error('Error fetching stories:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 개별 스토리 가져오기
     */
    async getStory(storyId) {
        try {
            const response = await fetch(`/api/stories/${storyId}/`, 
                this.getRequestConfig('GET')
            );

            return await response.json();
        } catch (error) {
            console.error('Error fetching story:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 현재 스토리 설정
     */
    setCurrentStory(storyId) {
        this.currentStoryId = storyId;
    }

    /**
     * 게임 상태 업데이트 이벤트 발생
     */
    dispatchGameStateUpdate(data) {
        const event = new CustomEvent('gameStateUpdate', {
            detail: {
                worldState: data.world_state || data.session_data?.world_data,
                characterState: data.character_state || data.session_data?.character_data,
                output: data.output,
                sessionId: this.sessionId,
                storyId: this.currentStoryId
            }
        });

        document.dispatchEvent(event);
    }

    /**
     * PyScript 연동을 위한 코드 실행
     */
    async executePyScriptCode(code) {
        // PyScript 환경에서 실행
        if (window.pyscript && window.pyscript.interpreter) {
            try {
                const result = await window.pyscript.interpreter.runPython(code);
                
                // 동시에 Django에도 저장
                await this.executeCode(code);
                
                return { success: true, result: result };
            } catch (error) {
                return { success: false, error: error.message };
            }
        } else {
            // PyScript가 없으면 Django API만 사용
            return await this.executeCode(code);
        }
    }
}

// 전역 인스턴스 생성
window.djangoGameAPI = new DjangoGameAPI();

// 게임 상태 업데이트 이벤트 리스너 등록
document.addEventListener('gameStateUpdate', function(event) {
    const { worldState, characterState, output } = event.detail;
    
    // 게임 UI 업데이트
    if (worldState && typeof updateWorldDisplay === 'function') {
        updateWorldDisplay(worldState);
    }
    
    if (characterState && typeof updateCharacterDisplay === 'function') {
        updateCharacterDisplay(characterState);
    }
    
    if (output && typeof updateTerminalOutput === 'function') {
        updateTerminalOutput(output);
    }
    
    console.log('Game state updated:', event.detail);
});

// 스토리 선택 이벤트 리스너
document.addEventListener('storySelected', async function(event) {
    const storyId = event.detail.storyId;
    
    if (storyId) {
        // 새 세션 생성
        const result = await window.djangoGameAPI.createSession(storyId);
        
        if (result.success) {
            console.log('New session created for story:', storyId);
            
            // 스토리별 초기 상태 설정
            if (result.session_data) {
                window.djangoGameAPI.dispatchGameStateUpdate(result);
            }
        } else {
            console.error('Failed to create session:', result.error);
        }
    }
});

// 페이지 로드시 기본 세션 생성
document.addEventListener('DOMContentLoaded', async function() {
    // 기본 세션 생성 (자유 모드)
    const result = await window.djangoGameAPI.createSession();
    
    if (result.success) {
        console.log('Default session created:', result.session_id);
    }
});

export default DjangoGameAPI;