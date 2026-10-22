import { createSlice, createAsyncThunk } from "@reduxjs/toolkit"
import { Source } from "@/types/source"
import { RootState } from "@/store/store"
import { toast } from "@/components/ui/toast"

interface createSourceArgs {
  token: string
}

export const createSource = createAsyncThunk<
  Source[],
  { token: string },
  { state: RootState }
>("admin/sourceCreate", async ({ token }: createSourceArgs, thunkAPI) => {
  // thunkAPI is used to access the state
  const state = thunkAPI.getState()
  const requestBody: Source[] = state.source.createSources.data // initialState is eliminated because its just a cover  over the state ,the runtime directly mounts all inside the intialstate into root so ->>> state.source.createSource.data    ---------->  .source is the key that is used to configure this slice in the global redux store.

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_GATEWAY_URL}/api/v1/datapipeline/admin/source`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      }
    )

    // if (!response.ok) {
    //   const errorData = await response.json()
    //   return thunkAPI.rejectWithValue(errorData.message || "Request failed")
    // }

    return response.json()
  } catch (error: any) {
    return thunkAPI.rejectWithValue(error.message)
  }
})


export const listTheSources = createAsyncThunk<
  Source[],
  { token: string }
>("admin/viewSources", async ({ token }: createSourceArgs, thunkAPI) => {
  // thunkAPI is used to access the state
 
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_GATEWAY_URL}/api/v1/datapipeline/admin/source`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    )

    // if (!response.ok) {
    //   const errorData = await response.json()
    //   return thunkAPI.rejectWithValue(errorData.message || "Request failed")
    // }
    console.log(response)
    return response.json()
  } catch (error: any) {
    return thunkAPI.rejectWithValue(error.message)
  }
})




export const sourceSlice = createSlice({
  name: "source",
  initialState: {
    createSources: {
      status: "idle",
      isLoading: false,
      data: [] as Source[],
      error: null,
    },
    isLoading: false,
    sources: [] as Source[],
  },
  reducers: {
    updateCreateStore: (state, action) => {
      const { sourceDetails } = action.payload
      state.createSources.data = [...state.createSources.data, sourceDetails] //sourceDetails will be added into the exisiting data
      console.log(state.createSources.data, "added data suuccessfully")
      toast.add({
        title: "Added the Source",
        description: "Source added successfully to the list",
        type: "info"

      })
    },

    removeTheCreateStoreSource: (state, action) => {
      const { index } = action.payload
      state.createSources.data = state.createSources.data.filter((_, i) => i !== index)
    },
  },

  extraReducers: (builder) => {
    builder
      .addCase(createSource.pending, (state) => {
        state.createSources.isLoading = true
      })
      .addCase(createSource.fulfilled, (state, action) => {
        state.createSources.isLoading = false
        const response = action.payload as any
        if (response.status_code === 201) {
          toast.add({
            title: "Populated the Source ",
            description: "Successfully populated the source to the data pipeline",
            type: "success"

          })
          state.createSources.data = [] // Clear the createSources data after successful submission
        }
        else if (response.status_code === 400 ) {
          toast.add({
            title: "Duplicate error",
            description: "Duplicate source found in the data pipeline",
            type: "error"
          })
        }
      })
      .addCase(createSource.rejected, (state, action) => {
        state.createSources.isLoading = false
      })
      .addCase(listTheSources.pending, (state) => {
        state.isLoading = true
        state.sources = []  // making the sources emptyyyyy, so that to get all the fresh data
      })
      .addCase(listTheSources.fulfilled, (state, action) => {
        state.isLoading = false
        
        const response = action.payload as any
        if (response.status_code === 200) {
          toast.add({
            title: "Here The Sources",
            description: "Successfully retrieved all the sources",
            type: "success"

          })
          state.sources = response.data.data
        }
        else if (response.status_code === 400 ) {
          toast.add({
            title: "Duplicate error",
            description: "Duplicate source found in the data pipeline",
            type: "error"
          })
        }
      })
  },
})

//used to export the actions -> the inbuild actions present to update the state.
export const { updateCreateStore,removeTheCreateStoreSource } = sourceSlice.actions //actions are the function that which is used here update our state
export default sourceSlice.reducer
