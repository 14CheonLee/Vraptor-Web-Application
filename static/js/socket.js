/**
 * Socket
 *
 * @TODO
 * Should Modify dummy data
 */

$(document).ready(function() {
    let socket_fan = io.connect(location.protocol + "//" + document.domain + ":" + location.port + "/fan");
    let socket_sensor = io.connect(location.protocol + "//" + document.domain + ":" + location.port + "/sensor");

    // Fan
    socket_fan.on("connect", function() {
        socket_fan.emit("message", {data: "[Socket_Fan] Connected ..."});
    });

    socket_fan.on("response", function(msg) {
        console.log(msg);
    });

    // Sensor
    socket_sensor.on("connect", function() {
        socket_sensor.emit("message", {data: "[Socket_Sensor] Connected ..."});
    });

    socket_sensor.on("response", function(msg) {
        console.log(msg);
    });

    // If click the button
    $("#fan_btn").click(function() {
        socket_fan.emit("message", {data: "Clicked fan button"});
    });

    $("#sensor_btn").click(function() {
        socket_sensor.emit("message", {data: "Clicked sensor button"});
    });

    $("#set_fan_speed_btn").click(function() {
        /**
         * @TODO
         * Should modify data
         */
        socket_fan.emit("set_fan_speed", {fan_number: 3, speed: 200});
    });

    $("#set_fan_mode_btn").click(function() {
        /**
         * @TODO
         * Should modify data
         */
        socket_fan.emit("set_fan_mode", {fan_auto_switch: true});
    });

    $("#get_all_data_btn").click(function() {
        /**
         * @TODO
         * Should modify data
         */
        socket_sensor.emit("get_all_data");
    });
});