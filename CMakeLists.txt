cmake_minimum_required(VERSION 3.10)

project(naraku_psp C)

add_executable(${PROJECT_NAME}
    main.c
)

target_compile_options(${PROJECT_NAME} PRIVATE
    -O2
    -Wall
    -Wextra
)

target_link_libraries(${PROJECT_NAME}
    pspdebug
    pspgu
    pspge
    pspdisplay
    pspctrl
    pspaudio
    pspkernel
)

set(NARAKU_XMB_ARGS)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/xmb/ICON0.PNG")
    list(APPEND NARAKU_XMB_ARGS ICON_PATH "${CMAKE_CURRENT_SOURCE_DIR}/xmb/ICON0.PNG")
endif()
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/xmb/PIC1.PNG")
    list(APPEND NARAKU_XMB_ARGS BACKGROUND_PATH "${CMAKE_CURRENT_SOURCE_DIR}/xmb/PIC1.PNG")
endif()
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/xmb/SND0.AT3")
    list(APPEND NARAKU_XMB_ARGS MUSIC_PATH "${CMAKE_CURRENT_SOURCE_DIR}/xmb/SND0.AT3")
endif()

create_pbp_file(
    TARGET ${PROJECT_NAME}
    TITLE "NARAKU PSP"
    VERSION 01.78
    ${NARAKU_XMB_ARGS}
)
