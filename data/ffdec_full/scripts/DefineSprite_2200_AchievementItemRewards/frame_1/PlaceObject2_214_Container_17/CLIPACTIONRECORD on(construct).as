on(construct){
   loop1:
   while(true)
   {
      if(!(0x1B797FD2 | 0x1B797FD2))
      {
         if(!(0x1B797FD2 | 0x1B797FD2))
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      addr10188:
      while(true)
      {
         if(!(getTimer() + 1))
         {
            §§push(getProperty(§§pop(), _X));
            break;
         }
         backgroundRenderer = "UI_AchievementRewardContainer";
         set("\x16\x10\x12","");
         dragAndDrop = false;
         enabled = false;
         set("\x18\x07\x0e",false);
         §§push("highlightRenderer");
         §§push("");
         if(ord("\x02"))
         {
            break loop1;
         }
         §§pop()[§§pop()] = §§pop();
      }
      return;
   }
   set(§§pop(),§§pop());
   set("\\",0);
   set("\x1d{invalid_utf8=150}\x07",2);
   set("\b\b\x01",true);
   set("","");
   §§goto(addr10188);
}
