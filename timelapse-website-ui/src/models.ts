import { z } from "zod"

export enum PictureIntent {
    TimeLapse,
    AdHoc,
}

export interface Picture {
    id: string
    dateTime: Date
    intent: PictureIntent
}

export function formatPicture(picture: Picture): string {
    return JSON.stringify(z.object({
        id: z.string(),
        dateTime: z.date(),
        intent: z.nativeEnum(PictureIntent),
    }).transform(({ id, dateTime, intent }) => ({
        id,
        intent: {
            [PictureIntent.TimeLapse]: "time_lapse",
            [PictureIntent.AdHoc]: "ad_hoc",
        }[intent],
        date_time: dateTime.toISOString(),
    })).parse(picture))
}

export function parsePicture(input: any): Picture {
    return z.object({
        id: z.string(),
        date_time: z.string(),
        intent: z
            .enum(["time_lapse", "ad_hoc"])
            .transform((value) => {
                return {
                    "time_lapse": PictureIntent.TimeLapse,
                    "ad_hoc": PictureIntent.AdHoc,
                }[value]
            })
    }).transform(({ id, date_time, intent }) => ({
        id,
        dateTime: new Date(date_time),
        intent,
    })).parse(input)
}


export interface ConfigValues {
    timeLapse: {
        enabled: boolean,
        wakeupTime: string | undefined, 
        delayInMinutes: number | undefined,
    },
}


export function parseConfigValues(input: any): ConfigValues {
    return z.object({
        time_lapse: z.object({
            enabled: z.boolean(),
            wakeup_time: z.string().optional(),
            delay_in_minutes: z.number().optional(),
        }),
    }).transform((pythonConfigValues) => ({
        timeLapse: {
            enabled: pythonConfigValues.time_lapse.enabled,
            wakeupTime: pythonConfigValues.time_lapse.wakeup_time,
            delayInMinutes: pythonConfigValues.time_lapse.delay_in_minutes,
        },
    })).parse(input)

}

export function formatConfigValues(configValues: ConfigValues): string {
    return JSON.stringify(z.object({
        timeLapse: z.object({
            enabled: z.boolean(),
            wakeupTime: z.string().optional(),
            delayInMinutes: z.number().optional(),
        }),
    }).transform(({ timeLapse }) => ({
        time_lapse: {
            enabled: timeLapse.enabled,
            wakeup_time: timeLapse.wakeupTime,
            delay_in_minutes: timeLapse.delayInMinutes,
        },
    })).parse(configValues))
}