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
import { source_scope } from "@/types/source"
import {
  IconFoldDown,
  IconGlobe,
  IconHome,
  IconList,
  IconUpload,
  IconWorld,
  IconWorldSearch,
  IconX,
} from "@tabler/icons-react"
import { useAuth } from "@clerk/nextjs"
import { Spinner } from "@/components/ui/spinner"

function Page() {
  // state configs to collect the most and essential state data
  const [newSource, setNewSource] = useState({
    source_name: '',
    source_url: '',
    source_type: '',
    source_nationality: '',
    source_scope: 'Technical',
  })

  const { getToken } = useAuth()
  // managing using redux toolkit
  const { createSources } = useAppSelector(state => state.source)
  const dispatch = useAppDispatch()

  const handleSourceAddition = (e) => {
    e.preventDefault()
    dispatch(updateCreateStore(  //dispatch funtion is used to tigger the functions defined inside the state to update the state variables
      {
        sourceDetails: newSource
      }
    ))

    //Cleaning the input fields after its upload function
    setNewSource({
      source_name: '',
      source_url: '',
      source_type: '',
      source_nationality: '',
      source_scope: 'Technical',
    })
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
                  value={newSource.source_name}
                  onChange={(e) => setNewSource({ ...newSource, source_name: e.target.value })}
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
                  value={newSource.source_url}
                  onChange={(e) => setNewSource({ ...newSource, source_url: e.target.value })}
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
                  value={newSource.source_type}
                  onChange={(e) => setNewSource({ ...newSource, source_type: e.target.value })}
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
                  value={newSource.source_nationality}
                  onChange={(e) => setNewSource({ ...newSource, source_nationality: e.target.value })}
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
                     {newSource.source_scope}
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuGroup>
                      <DropdownMenuItem onClick={() => {
                        setNewSource({ ...newSource, source_scope: 'Technical' })
                      }}>Technical</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setNewSource({ ...newSource, source_scope: 'Gaming' })
                      }}>Gaming</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setNewSource({ ...newSource, source_scope: 'Cinema' })
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
            <Button className="mt-5 flex w-full items-center gap-2 py-5 dark:bg-sidebar-accent bg-destructive" onClick={(e) => uploadTheSources(e)}>
              {
                createSources.isLoading ? <Spinner className="text-primary"/> : <IconUpload stroke={2} className="text-xl" />
              }

            Upload The Source
            </Button>
          </div>
        </div>
        <div className=" flex flex-col items-center gap-2 w-[60%] h-48 overflow-y-scroll no-scrollbar ">
          {
            createSources.data.map((source, index) => (
              <div key={index} className="flex items-center gap-2 w-full  justify-between">
                <DropdownMenu key={index}>
                  <DropdownMenuTrigger render={<Button className={"w-[90%]"} variant="secondary" />}>
                    {
                      source.source_name
                    }
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuGroup>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Source: </span>{source.source_name}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">URL: </span>{source.source_url}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Type: </span>{source.source_type}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Nationality: </span>{source.source_nationality}</DropdownMenuItem>
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
