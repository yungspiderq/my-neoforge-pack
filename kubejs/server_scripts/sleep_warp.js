// =====================================================================
//  Sleep-warp — фишка пака (замена SleepWarp (Updated), которого нет
//  под NeoForge 1.21.1: мод выходит только под Fabric/Quilt).
//  Конфиг: config/starlight-sleepwarp.json (перечитывается при /reload).
//
//  Логика: ночью, когда спит не меньше minSleepingPercent игроков,
//  время мира ускоряется на warpRatePerTick тиков за тик. На рассвете
//  (если clearWeatherOnWake) погода очищается. Одиночная игра = 100%.
// =====================================================================

const SW_CONFIG_PATH = 'config/starlight-sleepwarp.json'

function swLoadConfig() {
    let cfg = null
    try {
        cfg = JsonIO.read(SW_CONFIG_PATH)
    } catch (e) {
        cfg = null
    }
    if (!cfg) {
        cfg = { enabled: true, minSleepingPercent: 50, warpRatePerTick: 60,
                clearWeatherOnWake: true, broadcastMessages: true }
        JsonIO.write(SW_CONFIG_PATH, cfg)
    }
    return cfg
}

global.swCfg = swLoadConfig()
global.swNotified = false

ServerEvents.tick(event => {
    const server = event.server
    if (server.tickCount % 10 !== 0) return
    const cfg = global.swCfg
    if (!cfg || cfg.enabled === false) return
    const level = server.getLevel('minecraft:overworld')
    if (!level) return
    const players = server.players
    const online = players.length
    if (online === 0) return
    const tod = level.time % 24000
    const isNight = tod >= 13000 && tod <= 23400
    let sleeping = 0
    players.forEach(p => { if (p.isSleeping()) sleeping++ })
    const percent = (sleeping * 100) / online
    if (isNight && sleeping > 0 && percent >= (cfg.minSleepingPercent ?? 50)) {
        if (!global.swNotified) {
            global.swNotified = true
            if (cfg.broadcastMessages !== false) {
                server.runCommandSilent('tellraw @a {"text":"☾ Спящих достаточно — ночь ускоряется…","color":"aqua"}')
            }
        }
        level.time = level.time + (cfg.warpRatePerTick ?? 60)
    } else if (!isNight) {
        if (global.swNotified) {
            global.swNotified = false
            if (cfg.clearWeatherOnWake !== false && (level.rainTime > 0 || level.thunderTime > 0)) {
                server.runCommandSilent('weather clear')
            }
            if (cfg.broadcastMessages !== false) {
                server.runCommandSilent('tellraw @a {"text":"☀ Рассвет. Спасибо, что спали дома.","color":"yellow"}')
            }
        }
    }
})
