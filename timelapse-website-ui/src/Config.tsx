import { Client } from "./client"
import { useState, Dispatch, SetStateAction, useEffect, useCallback } from "react"

export interface ConfigProps {

    client: Client,

}

enum Type {
    TEXT,
    TOGGLE,
}

interface Entry {
    name: string,
    label: string,
    type: Type,
}

interface Group {
    name: string,
    label: string,
    entries: Entry[]
}

const GROUPS: Group[] = [
    {
        label: "Hotspot",
        name: "hotspot",
        entries: [
            {
                name: "enabled",
                label: "Activé",
                type: Type.TOGGLE,
            },
            {
                name: "ssid",
                label: "SSID",
                type: Type.TEXT,
            },
            {
                name: "password",
                label: "Clé WPA",
                type: Type.TEXT,
            },
        ],
    },
    {
        label: "Time Lapse",
        name: "timeLapse",
        entries: [
            {
                name: "enabled",
                label: "Activé",
                type: Type.TOGGLE,
            },
            {
                name: "wakeupTime",
                label: "Heure de réveil",
                type: Type.TEXT,
            },
        ]
    },
    {
        label: "Bluetooth",
        name: "bluetooth",
        entries: [
            {
                name: "enabled",
                label: "Activé",
                type: Type.TOGGLE,
            },
            {
                name: "deviceName",
                label: "Nom du device",
                type: Type.TEXT,
            },
        ]
    }
]

interface InputProps {

    id: string,
    type: Type,
    onChange: (value: string | boolean) => void,
    initialValue?: string | boolean,

}

function Input({ type, id, onChange, initialValue }: InputProps) {
    switch (+type) {
        case Type.TEXT:
            return (
                <input value={ initialValue === undefined ? undefined : `${initialValue}` }onChange={ (event) => onChange(event.target.value) }  type="text" id="first_name" className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" />
            )

        case Type.TOGGLE:
            return (
                <label className="relative inline-flex items-center cursor-pointer">
                    <input checked={ typeof initialValue === "boolean" ? initialValue : false } onChange={ (event) => onChange(event.target.checked) } id={ id }type="checkbox" value="" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
            )

        default:
            return null;
    }
}


export default function ConfigForm({ client }: ConfigProps) {

    const valuesByKey = new Map<string, string | boolean | null>()
    const setValuesByKey = new Map<string, Dispatch<SetStateAction<string | boolean | null>>>()

    for (const { name: groupName, entries: groupEntries } of GROUPS) {
        for (const { name: entryName } of groupEntries) {
            const key = `${groupName}-${entryName}`
            const [value, setValue] = useState<string | boolean | null>(null)
            valuesByKey.set(key, value)
            setValuesByKey.set(key, setValue)
        }
    }

    const readConfigValues = useCallback(async () => {
        const configValues = await client.readConfigValues()
        console.log(configValues)
        return configValues
    }, [])

    useEffect(() => {
        ( async () => {
            console.log("We are here! ")
            const configValues = await readConfigValues()
            valuesByKey.set("hotspot-enabled", configValues.hotspot.enabled)
            valuesByKey.set("hotspot-ssid", configValues.hotspot.ssid)
            valuesByKey.set("hotspot-password", configValues.hotspot.password === undefined ? null : configValues.hotspot.enabled )
            valuesByKey.set("timeLapse-enabled", configValues.timeLapse.enabled)
        })();
    }, 
        [
            readConfigValues,
            // ...Array.from(setValuesByKey.values()),
        ]
    )

    

    function displayValues() {
        console.log(valuesByKey);
    }


    return (
        <form onSubmit={ (event) => event.preventDefault() } className="flex flex-col w-full py-2 px-2">
            { GROUPS.map(({ label: groupLabel, name: groupName, entries: groupEntries }) => (
                <fieldset key={ groupName } className="border border-solid border-gray-300 p-3 mb-2 rounded-lg">
                    <legend className="text-gray-500">{ groupLabel }</legend>
                    <div className="flex-1 flex flex-col gap-2 justify-center">
                        { groupEntries.map(({ name: entryName, label: entryLabel, type: entryType }) => (
                            <div key={ `${groupName}-${entryName}` } className="flex-1 flex flex-col sm:flex-row items-center justify-center">
                                <label htmlFor={ `${groupName}-${entryName}` } className="block w-full sm:w-1/6 text-center sm:text-right pr-2">{ entryLabel }&nbsp;:&nbsp;</label>
                                <div className="flex-1 flex flex-col w-full sm:w-5/6 text-center sm:text-left sm:items-left items-center sm:items-start">
                                    <Input initialValue={ valuesByKey.get(`${groupName}-${entryName}`)! } onChange={ (value) => {
                                        const setValue = setValuesByKey.get(`${groupName}-${entryName}`)
                                        if (setValue !== undefined) {
                                            console.log("Coucou")
                                            setValue(value)
                                        }
                                     } } type={ entryType } id={ `${groupName}-${entryName}` } />
                                </div>
                            </div>
                        ) ) }
                    </div>
                </fieldset>
            ) ) }
            <button type="submit" onClick={ () => displayValues() } className="mt-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Submit</button>
        </form>
    )

}