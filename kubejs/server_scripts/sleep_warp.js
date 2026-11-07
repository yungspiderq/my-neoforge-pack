// =====================================================================
//  Sleep-warp — фишка пака (замена SleepWarp (Updated), которого нет
//  под NeoForge 1.21.1). Работает НА СЕРВЕРЕ: в одиночной игре это
//  встроенный сервер, в мультиплеере — тот сервер, где лежит пак
//  (версия скриптов >= 1.6.5!). Конфиг: config/starlight-sleepwarp.json,
//  перечитывается при /reload и рестарте.
//
//  Условие варпа: ночь И спит >= minSleepingPlayers И доля спящих
//  (без зрителей) >= minSleepingPercent. Дефолт: достаточно одного.
//  Диагностика:_reason-строки в лого сервера, когда кто-то спит,
//  но варп не включился.
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
        cfg = { enabled: true, minSleepingPlayers: 1, minSleepingPercent: 0,
                warpRatePerTick: 60, clearWeatherOnWake: true, broadcastMessages: true }
        try { JsonIO.write(SW_CONFIG_PATH, cfg) } catch (e) { /* readonly? не страшно */ }
    }
    return cfg
}

// global в server-скриптах KubeJS 2101 недоступен для записи — var уровня скрипта
var swCfg = swLoadConfig()
var swNotified = false
var swReasonLogged = false

ServerEvents.tick(event => {
    const server = event.server
    if (server.tickCount % 10 !== 0) return
    const cfg = swCfg
    if (!cfg || cfg.enabled === false) return
    const level = server.getLevel('minecraft:overworld')
    if (!level) return
    const players = server.players
    let online = 0
    let sleeping = 0
    players.forEach(p => {
        let spectator = false
        try { spectator = p.getGameMode() === 'spectator' } catch (e) { spectator = false }
        if (spectator) return
        online++
        if (p.isSleeping()) sleeping++
    })
    if (online === 0) return
    const tod = level.time % 24000
    const isNight = tod >= 13000 && tod <= 23400
    const percent = (sleeping * 100) / online
    const minPlayers = cfg.minSleepingPlayers ?? 1
    const minPercent = cfg.minSleepingPercent ?? 0
    if (isNight && sleeping > 0) {
        if (sleeping >= minPlayers && percent >= minPercent) {
            if (!swNotified) {
                swNotified = true
                swReasonLogged = false
                if (cfg.broadcastMessages !== false) {
                    server.runCommandSilent('tellraw @a {"text":"☾ Спящих достаточно — ночь ускоряется…","color":"aqua"}')
                }
                console.info('[sleepwarp] warp: online=' + online + ' sleeping=' + sleeping +
                             ' percent=' + percent.toFixed(0))
            }
            level.time = level.time + (cfg.warpRatePerTick ?? 60)
        } else if (!swReasonLogged) {
            swReasonLogged = true
            console.info('[sleepwarp] спят ' + sleeping + '/' + online + ' (' + percent.toFixed(0) +
                         '%), нужно: >= ' + minPlayers + ' и >= ' + minPercent +
                         '% — варп выключен конфигом config/starlight-sleepwarp.json')
        }
    } else if (!isNight) {
        if (swNotified) {
            swNotified = false
            swReasonLogged = false
            if (cfg.clearWeatherOnWake !== false && (level.rainTime > 0 || level.thunderTime > 0)) {
                server.runCommandSilent('weather clear')
            }
            if (cfg.broadcastMessages !== false) {
                server.runCommandSilent('tellraw @a {"text":"☀ Рассвет. Спасибо, что спали дома.","color":"yellow"}')
            }
        }
    }
})
