"use client"
import React from "react"
import { useState } from "react"

import { Input } from "@/components/ui/input"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

import { useAppDispatch, useAppSelector } from "@/lib/redux/hook"
import { createSource, updateCreateStore, removeTheCreateStoreSource } from "@/features/sourceSlice"
import { Source, source_scope } from "@/types/source"
import {
  IconFoldDown,
  IconGlobe,
  IconHome,
  IconList,
  IconPencil,
  IconUpload,
  IconWorld,
  IconWorldSearch,
  IconX,
} from "@tabler/icons-react"
import { useAuth } from "@clerk/nextjs"
import { Badge } from "@/components/ui/badge"

function Page() {
  // state configs to collect the most and essential state data
  const [sourceName, setSourceName] = useState('')
  const [sourceURL, setSourceURL] = useState('')
  const [sourcetype, setSourcetype] = useState('')
  const [sourceNationality, setSourceNationality] = useState('')
  const [sourceScope, setSourceScope] = useState<source_scope>('Technical')

  const { getToken, isLoaded, isSignedIn } = useAuth()
  const { createSources } = useAppSelector(state => state.source)
  const dispatch = useAppDispatch()

  const handleSourceAddition = (e) => {
    e.preventDefault()
    const source_dict = {
      source_name: sourceName,
      source_url : sourceURL,
      source_type : sourcetype,
      nationality : sourceNationality,
      source_scope : sourceScope,
    }
    dispatch(updateCreateStore(  //dispatch funtion is used to tigger the functions defined inside the state to update the state variables
      {
        sourceDetails: source_dict
      }
    ))

    //Cleaning the input fields after its upload function
    setSourceName('')
    setSourceURL('')
    setSourcetype('')
    setSourceScope('Technical')
    setSourceNationality('')
  }

  const uploadTheSources = async (e) => {
    e.preventDefault()
    const clerkJwtToken = await getToken()

    dispatch(
      createSource({
        token:clerkJwtToken ||''
      })
    )
  }

  const handleRemoveSource = (index: any) => {
    dispatch(removeTheCreateStoreSource({ index }))
  }


  return (
    <div className="mx-auto flex items-center justify-between gap-3 px-16">
      <div className="flex h-screen w-[48%] flex-col justify-center">
        <div className="my-20">
          <h1 className="text-4xl font-bold">Add Sources</h1>
          <p className="text-lg font-light text-gray-600 italic">
            Add new sources to fuel up the pulsegrid data pipeline.
          </p>
        </div>
        <div className="my-10 w-[60%]">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2 w-full">
              <div className="flex items-center gap-2 w-full">
                <div className="border-color-border flex h-10 w-12 items-center justify-center rounded-full border dark:bg-input/30">
                  <IconGlobe className="text-2xl" stroke={2} />
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full rounded-2xl py-5"
                  placeholder="eg:- TechCrunch"
                  value={sourceName}
                  onChange={(e) => setSourceName(e.target.value)}
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="border-color-border flex h-10 w-12 items-center justify-center rounded-full border dark:bg-input/30">
                  <IconWorldSearch className="text-2xl" stroke={2} />
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full rounded-2xl py-5"
                  placeholder="eg:- www.TechCrunch.com"
                  value={sourceURL}
                  onChange={(e) => setSourceURL(e.target.value)}
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="border-color-border flex h-10 w-12 items-center justify-center rounded-full border dark:bg-input/30">
                  <IconWorld className="text-2xl" stroke={2} />
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full rounded-2xl py-5"
                  placeholder="eg:- International or National"
                  value={sourcetype}
                  onChange={(e) => setSourcetype(e.target.value)}
                />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="border-color-border flex h-10 w-12 items-center justify-center rounded-full border dark:bg-input/30">
                  <IconHome className="text-2xl" stroke={2} />
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full rounded-2xl py-5"
                  placeholder="eg:- India or America or Japan"
                  value={sourceNationality}
                  onChange={(e) => setSourceNationality(e.target.value)}
                />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="border-color-border flex h-10 w-11 items-center justify-center rounded-full border dark:bg-input/30">
                  <IconFoldDown className="text-2xl" stroke={2} />
                </div>
                <DropdownMenu >
                  <DropdownMenuTrigger render={<Button variant="outline" className={"w-[90%] text-left"}/>} className={"text-left"}>
                     {sourceScope}
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuGroup>
                      <DropdownMenuItem onClick={() => {
                        setSourceScope('Technical')
                      }}>Technical</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setSourceScope('Gaming')
                      }}>Gaming</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setSourceScope('Cinema')
                      }}>Cinema</DropdownMenuItem>
                    </DropdownMenuGroup>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </div>
          <div className="w-[50%] flex items-center justify-between gap-1">
          <Button className="mt-5 flex w-full items-center gap-2 py-5" onClick={(e) => handleSourceAddition(e)}>
            <IconList stroke={2} className="text-xl" />
            Add Source To The List
          </Button>
          <Button className="mt-5 flex w-full items-center gap-2 py-5 bg-sidebar-accent" onClick={(e) => uploadTheSources(e)}>
            <IconUpload stroke={2} className="text-xl" />
            Upload The Source
            </Button>
          </div>
        </div>
        <div className=" flex flex-col items-center gap-2 w-[60%] h-48 overflow-y-scroll no-scrollbar ">
          {
            createSources.data.map((source, index) => (
              <div key={index} className="flex items-center gap-2 w-full  justify-between">
                <DropdownMenu key={index}>
                  <DropdownMenuTrigger render={<Button className={"w-[80%]"} variant="secondary" />}>
                    {
                      source.source_name
                    }
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuGroup>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Source: </span>{source.source_name}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">URL: </span>{source.source_url}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Type: </span>{source.source_type}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Nationality: </span>{source.nationality}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Scope: </span>{source.source_scope}</DropdownMenuItem>
                    </DropdownMenuGroup>
                  </DropdownMenuContent>
                </DropdownMenu>
                <div className="flex items-center gap-2">
                  <div className="py-1 px-2 rounded-xl bg-sidebar-accent" onClick={() => {
                    handleRemoveSource(index)
                  }}>
                    <IconX className="text-destructive" stroke={2} />
                  </div>
                  <div className="py-1 px-2 rounded-xl bg-sidebar-accent-foreground">
                    <IconPencil className="text-primary" stroke={2} />
                  </div>
                </div>
              </div>
            ))
          }
        </div>
      </div>
      <div>
        {/*<h1 className="text-4xl font-bold">Add Sources</h1>
        <p className="text-lg font-light text-gray-600 italic">
          Add new sources to fuel up the pulsegrid data pipeline.
        </p>*/}
      </div>
    </div>
  )
}

export default Page
