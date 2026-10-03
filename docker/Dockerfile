# syntax=docker/dockerfile:1.7
FROM osrf/ros:lyrical-desktop

ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=${USER_UID}
ARG RPP_DEV_REPOSITORY=git@github.com:coe-marble/rpp_dev.git
ARG RPP_DEV_REF=main

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=lyrical
ENV RPP_USE_ROS2_COMPILATION=true

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        bash-completion \
        build-essential \
        ca-certificates \
        capnproto=1.1.0-2.1 \
        clang-format \
        clang-tidy \
        cmake \
        gdb \
        git \
        less \
        libcapnp-dev=1.1.0-2.1 \
        libspdlog-dev \
        nlohmann-json3-dev \
        openssh-client \
        pybind11-dev \
        python3-colcon-argcomplete \
        python3-colcon-common-extensions \
        python3-dev \
        python3-pip \
        python3-pyqt6 \
        python3-venv \
        sudo \
    && rm -rf /var/lib/apt/lists/*

RUN if ! getent group "${USER_GID}" > /dev/null; then groupadd --gid "${USER_GID}" "${USERNAME}"; fi \
    && if ! id -u "${USERNAME}" > /dev/null 2>&1; then useradd --uid "${USER_UID}" --gid "${USER_GID}" --create-home --shell /bin/bash "${USERNAME}"; fi \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${USERNAME}" \
    && chmod 0440 "/etc/sudoers.d/${USERNAME}"

RUN python3 -m venv --system-site-packages /opt/rpp-venv \
    && chown -R "${USERNAME}:${USER_GID}" /opt/rpp-venv

ENV PATH="/opt/rpp-venv/bin:${PATH}"

ENV PYTHONPATH="/opt/rpp-venv/lib/python3.14/site-packages:\
/workspaces/rpp/ros2_ws/src/rpp_dev/src/rpp_py:\
/workspaces/rpp/ros2_ws/src/rpp_libraries/more_common:${PYTHONPATH}"

RUN --mount=type=ssh \
    install -d -m 0700 /root/.ssh \
    && ssh-keyscan github.com > /root/.ssh/known_hosts \
    && mkdir -p /workspaces/rpp/ros2_ws/src/rpp_libraries \
    && git clone --branch "${RPP_DEV_REF}" "${RPP_DEV_REPOSITORY}" /workspaces/rpp/ros2_ws/src/rpp_dev \
    && cd /workspaces/rpp/ros2_ws/src/rpp_dev && source /opt/ros/lyrical/setup.bash && ./setup.sh \
    && git clone --recurse-submodules git@github.com:MOREnvironment/more_common.git /workspaces/rpp/ros2_ws/src/rpp_libraries/more_common \
    && git clone --recurse-submodules git@github.com:MOREnvironment/more_sensors.git /workspaces/rpp/ros2_ws/src/rpp_libraries/more_sensors \
    && git clone --recurse-submodules git@github.com:MOREnvironment/more_dynamics.git /workspaces/rpp/ros2_ws/src/rpp_libraries/more_dynamics \
    && git clone --recurse-submodules git@github.com:MOREnvironment/more_simulation.git /workspaces/rpp/ros2_ws/src/rpp_libraries/more_simulation \
    && git clone --recurse-submodules git@github.com:coe-marble/rpp_control.git /workspaces/rpp/ros2_ws/src/rpp_libraries/rpp_control \
    && git clone --recurse-submodules git@github.com:coe-marble/marble_control_msgs.git /workspaces/rpp/ros2_ws/src/marble_control_msgs \
    # && git clone --recurse-submodules git@github.com:coe-marble/rpp_localization.git /workspaces/rpp/ros2_ws/src/rpp_libraries/rpp_localization \
    && chown -R "${USERNAME}:${USER_GID}" /workspaces

USER ${USERNAME}


RUN cd /workspaces/rpp/ros2_ws \
    && source /opt/ros/lyrical/setup.bash \
    && pip install --no-cache-dir -e /workspaces/rpp/ros2_ws/src/rpp_libraries/more_common \
    && pip install --no-cache-dir -e /workspaces/rpp/ros2_ws/src/rpp_libraries/more_sensors \
    && pip install --no-cache-dir -e /workspaces/rpp/ros2_ws/src/rpp_libraries/more_dynamics \
    && pip install --no-cache-dir -e /workspaces/rpp/ros2_ws/src/rpp_libraries/more_simulation \
    && colcon build --base-paths src/rpp_dev/src --packages-up-to rpp_cpp --symlink-install --cmake-args -DBUILD_TESTING=OFF \
    && colcon build --packages-select marble_control_msgs --symlink-install --cmake-args -DBUILD_TESTING=OFF \
    && source /workspaces/rpp/ros2_ws/install/setup.bash \
    && rpp init-home \
    && rpp library register /workspaces/rpp/ros2_ws/src/rpp_libraries/more_sensors --link \
    && rpp library register /workspaces/rpp/ros2_ws/src/rpp_libraries/more_dynamics --link \
    && rpp library register /workspaces/rpp/ros2_ws/src/rpp_libraries/more_simulation --link \
    && rpp library register /workspaces/rpp/ros2_ws/src/rpp_libraries/rpp_control --link \
    && colcon build --symlink-install --cmake-args -DBUILD_TESTING=OFF \
    && source /workspaces/rpp/ros2_ws/install/setup.bash

RUN printf '%s\n' \
        'source /opt/ros/lyrical/setup.bash' \
        'if [ -f /workspaces/rpp/ros2_ws/install/setup.bash ]; then' \
        '    source /workspaces/rpp/ros2_ws/install/setup.bash' \
        'fi' \
        'source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash' \
        >> "/home/${USERNAME}/.bashrc"

WORKDIR /workspaces/rpp_dev
