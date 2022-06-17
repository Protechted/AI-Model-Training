<template>
  <Renderer ref="rendererC" antialias :orbit-ctrl="{ enableDamping: true }" resize="window">
    <Camera :position="{x: 10, y:0, z:5}" :look-at="handC"/>
    <Scene background="#626e8a">
      <HemisphereLight />
      <FbxModel ref="handC" :scale="{ x: 0.01, y: 0.01, z: 0.01 }" :position="{ x: -3, y: 0, z:-4 }" :rotation="{ x: 1.5, y: 0, z: 5}"
      src="/src/HAND.fbx"/>
    </Scene>
  </Renderer>
</template>



<script setup>
import { ref, onMounted } from 'vue'
import { Box, Camera, LambertMaterial, PointLight, Renderer, Scene} from 'troisjs'
import Websocket from 'isomorphic-ws'

const ws = new Websocket("ws://127.0.0.1:5300/")

const rendererC = ref()
const handC = ref()

let quaternion = [0, 0, 0, 1];

ws.onopen = function open() {
  console.log('connected');
  ws.send("live");
};

ws.onclose = function close() {
  console.log('disconnected');
};

// function onReady
function onReady(hand) {
  // scale down the model
  hand.scale.multiplyScalar(0.01)
  // add the model to the scene
}

ws.onmessage = function incoming(data) {
  let msg = data.data.slice(9);
  // try to parse JSON else log the message
  let json = null;
  // if message is not empty
  if (msg.length > 0) {
    json = JSON.parse(msg);}
  quaternion = [json.qx, json.qy, json.qz, json.qw];
  };

onMounted(() => {
  const renderer = rendererC.value
  const hand = handC.value["scene"]["quaternion"]

  renderer.onBeforeRender(() => {
    hand.set(quaternion[2], quaternion[1], quaternion[3], quaternion[0])
  })
})
</script>

<style>
body {
  margin: 0;
}
canvas {
  display: block;
}
</style>