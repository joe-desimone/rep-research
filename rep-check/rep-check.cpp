// rep-check.cpp
// Author: Joe Desimone https://x.com/dez_
// Note: If SAC is enabled (evaluation or enforcement) this will return SAC trust level.
// Otherwise, it returns SmartScreen trust level.

#include <Windows.h>
#include <stdio.h>
#include <stdint.h>

typedef struct
{
    uint32_t sz;
    uint32_t trustLevel;
    uint64_t ttl;
} params_t;

typedef struct
{
    uint32_t first;
    uint32_t second;
    uint32_t szData;
    uint32_t pad;
    void *   data;
} extraInfo_t;


typedef  __int64 (*MpQueryFileTrustByHandle2_t)(HANDLE hFile, void * a2, void* a3, 
    params_t* pParams, size_t * count, extraInfo_t ** extraInfo);

int main(int argc, char* argv[])
{
    params_t params = { 0x10, 0, 0};
    size_t count = 0;
    extraInfo_t* pExtraInfo = 0;
    uint64_t retVal = 0;
    HANDLE hFile = 0;
    MpQueryFileTrustByHandle2_t MpQueryFileTrustByHandle2 = 0;

    if (argc < 2)
    {
        printf("Usage: %s <path to file>\n", argv[0]);
        return -1;
    }

    MpQueryFileTrustByHandle2 = (MpQueryFileTrustByHandle2_t)GetProcAddress(
        LoadLibraryA("C:\\Program Files\\Windows Defender\\MpClient.dll"), 
        "MpQueryFileTrustByHandle2");

    if (!MpQueryFileTrustByHandle2)
    {
        printf("MpQueryFileTrustByHandle2 not found\n");
        return -1;
    }

    hFile = CreateFileA(argv[1], GENERIC_READ, FILE_SHARE_READ, 0, OPEN_EXISTING, 0, 0);
    printf("File handle: %p\n", hFile);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        printf("Error opening file: %x\n", GetLastError());
        return -1;
    }

    retVal = MpQueryFileTrustByHandle2(hFile, 0, 0, &params, &count, &pExtraInfo);

    if (retVal == 0)
    {
        printf("params: rep: %d, ttl: %llx ms, extra info count: %lld\n",
            params.trustLevel, params.ttl, count);

        if (count)
        {
            printf("extraInfo: %d, %d, %d, %p -> %x\n", pExtraInfo->first, pExtraInfo->second,
                pExtraInfo->szData, pExtraInfo->data, *(DWORD*)pExtraInfo->data);
        }

        if (params.trustLevel == -3)
            printf("Rep: PUA\n");
        else if (params.trustLevel == -2)
            printf("Rep: Malicious\n");
        else if (params.trustLevel == -1)
            printf("Rep: Unknown/Unattainable\n");
        else if (params.trustLevel == 0)
            printf("Rep: good\n");
        else if (params.trustLevel == 1)
            printf("Rep: high\n");
        else
            printf("Unknown Rep: %d\n", params.trustLevel);
    }
    else
    {
        printf("Error code: %llx\n", retVal);
    }

    CloseHandle(hFile);
}
